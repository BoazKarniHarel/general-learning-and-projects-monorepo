import os
import re
import subprocess
import sys

try:
    import tomllib  # Python 3.11+
except ImportError:
    print("Python 3.11+ is required for tomllib.")
    sys.exit(1)

try:
    from packaging.specifiers import SpecifierSet
    from packaging.version import InvalidVersion, Version
except ImportError:
    if not os.environ.get("UV_PIPX_RUNNING"):
        cmd = ["uv", "pipx", "run", "packaging", sys.executable] + sys.argv
        os.execvp("uv", cmd)
    from packaging.specifiers import SpecifierSet
    from packaging.version import InvalidVersion, Version

def parse_pkg_and_constraint(arg):
    # Match things like "pandas>=1.0.1", "numpy==1.3.2", "scipy"
    m = re.match(r"^([a-zA-Z0-9_\-]+)([<>=!~^].*)?$", arg)
    if m:
        print(f"package: {m.group(1)}, constraint: {m.group(2)}")
        pkg = m.group(1)
        constraint = m.group(2) or ""
        return pkg, constraint
    else:
        return arg, ""

def find_pyprojects(root):
    pyprojects = []
    for dirpath, dirnames, filenames in os.walk(root):
        if "pyproject.toml" in filenames:
            pyprojects.append(os.path.join(dirpath, "pyproject.toml"))
    return pyprojects

def get_package_versions(pyproject_path, pkg_name):
    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)
    versions = []
    deps = data.get("project", {}).get("dependencies", [])
    for dep in deps:
        if dep.lower().startswith(pkg_name.lower()):
            parts = dep.split(" ", 1)
            if len(parts) == 2:
                versions.append(parts[1].strip())
            else:
                versions.append("")
    opt_deps = data.get("project", {}).get("optional-dependencies", {})
    for group in opt_deps.values():
        for dep in group:
            if dep.lower().startswith(pkg_name.lower()):
                parts = dep.split(" ", 1)
                if len(parts) == 2:
                    versions.append(parts[1].strip())
                else:
                    versions.append("")
    return versions

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Sync uv add across monorepo projects.")
    parser.add_argument("package_and_constraint", help="Package name, possibly with version constraint (e.g. pandas>=1.0.1)")
    parser.add_argument("--group", default=None, help="Optional dependency group")
    args = parser.parse_args()

    pkg, constraint = parse_pkg_and_constraint(args.package_and_constraint)
    group = args.group

    repo_root = os.path.dirname(os.path.abspath(__file__))
    cwd = os.getcwd()

    pyprojects = find_pyprojects(repo_root)

    found_versions = []
    for pyproject in pyprojects:
        specs = get_package_versions(pyproject, pkg)
        found_versions.extend(specs)
    found_versions = [v for v in found_versions if v]

    parsed_versions = []
    spec = SpecifierSet(constraint) if constraint else None
    for v in found_versions:
        try:
            version = Version(v.lstrip("=<>!~^"))
            if not spec or version in spec:
                parsed_versions.append(version)
        except InvalidVersion:
            continue

    if parsed_versions:
        latest = max(parsed_versions)
        print(f"Found versions: {', '.join(str(v) for v in parsed_versions)}")
        print(f"Using latest matching version: {latest}")
        uv_cmd = ["uv", "add"]
        if group:
            uv_cmd += ["--group", group]
        uv_cmd.append(f"{pkg}=={latest}")
        print("Running:", " ".join(uv_cmd))
        subprocess.run(uv_cmd, cwd=cwd)
    elif found_versions:
        print(f"Found versions of {pkg} in other projects, but none satisfy constraint '{constraint}'.")
        print("Consider updating other projects, relaxing your constraint, or running 'uv add' manually.")
        sys.exit(1)
    else:
        print(f"No existing installations of {pkg} found. Running uv add with your input.")
        uv_cmd = ["uv", "add"]
        if group:
            uv_cmd += ["--group", group]
        if constraint:
            uv_cmd.append(f"{pkg}{constraint}")
        else:
            uv_cmd.append(pkg)
        print("Running:", " ".join(uv_cmd))
        subprocess.run(uv_cmd, cwd=cwd)

if __name__ == "__main__":
    main()