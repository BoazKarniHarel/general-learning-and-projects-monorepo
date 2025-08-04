import os
import re
import sys

# Ensure loguru is available (ephemeral install if needed)
try:
    from loguru import logger
except ImportError:
    if not os.environ.get("UV_PIPX_RUNNING"):
        cmd = ["uv", "pipx", "run", "loguru", sys.executable] + sys.argv
        os.execvp("uv", cmd)
        from loguru import logger

try:
    import tomllib  # Python 3.11+
except ImportError:
    print("Python 3.11+ is required for tomllib.")
    sys.exit(1)

def find_pyprojects(root):
    pyprojects = []
    for dirpath, dirnames, filenames in os.walk(root):
        if "pyproject.toml" in filenames:
            pyprojects.append(os.path.join(dirpath, "pyproject.toml"))
    return pyprojects

def extract_deps(pyproject_path):
    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)
    deps = []
    # [project] dependencies
    for dep in data.get("project", {}).get("dependencies", []):
        pkg, ver = parse_dep(dep)
        deps.append((pkg, ver))
    # [project.optional-dependencies]
    for group in data.get("project", {}).get("optional-dependencies", {}).values():
        for dep in group:
            pkg, ver = parse_dep(dep)
            deps.append((pkg, ver))
    return deps

def parse_dep(dep):
    # Match things like "pandas>=1.0.1", "numpy==1.3.2", "scipy"
    m = re.match(r"^([a-zA-Z0-9_\-]+)([<>=!~^].*)?$", dep)
    if m:
        pkg = m.group(1).lower()
        ver = m.group(2) or ""
        return pkg, ver
    return dep.lower(), ""

def main():
    repo_root = os.path.dirname(os.path.abspath(__file__))
    pyprojects = find_pyprojects(repo_root)

    # {package: {version: [project1, project2, ...]}}
    pkg_versions = {}

    for pyproject in pyprojects:
        project_name = os.path.basename(os.path.dirname(pyproject))
        for pkg, ver in extract_deps(pyproject):
            if pkg not in pkg_versions:
                pkg_versions[pkg] = {}
            if ver not in pkg_versions[pkg]:
                pkg_versions[pkg][ver] = []
            pkg_versions[pkg][ver].append(project_name)

    for pkg, versions in pkg_versions.items():
        if len(versions) > 1:
            version_list = [f"{ver or '(no version constraint)'}: {', '.join(projs)}" for ver, projs in versions.items()]
            logger.warning(
                f"Package '{pkg}' is installed with multiple versions/constraints:\n" +
                "\n".join(version_list)
            )

if __name__ == "__main__":
    main()
