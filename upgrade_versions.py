import json
import os
import sys
import argparse
from pathlib import Path

def upgrade_version(repo_root, from_version, to_version):
    repo_root = Path(repo_root).resolve()
    print(f"Upgrading versions from {from_version} to {to_version} in {repo_root}")

    package_json_files = list(repo_root.rglob("package.json"))
    package_json_files = [f for f in package_json_files if "node_modules" not in str(f)]

    # First, collect all internal package names
    internal_packages = set()
    for p_path in package_json_files:
        try:
            with open(p_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'name' in data:
                    internal_packages.add(data['name'])
        except Exception as e:
            print(f"Error reading {p_path}: {e}")

    updated_count = 0
    for p_path in package_json_files:
        try:
            with open(p_path, 'r', encoding='utf-8') as f:
                content = f.read()
                data = json.loads(content)

            changed = False

            # Update version field
            if data.get('version') == from_version:
                data['version'] = to_version
                changed = True

            # Update dependencies
            for dep_type in ['dependencies', 'devDependencies', 'peerDependencies']:
                if dep_type in data:
                    for dep_name, dep_version in data[dep_type].items():
                        if dep_name in internal_packages and (dep_version == from_version or dep_version == f"workspace:{from_version}"):
                            # If it's workspace:*, it usually doesn't need version upgrade, 
                            # but if it's a specific version, we update it.
                            # Some monorepos use workspace:* or workspace:^
                            pass # Handled below if it's a specific version
                        
                        if dep_version == from_version:
                            data[dep_type][dep_name] = to_version
                            changed = True
                        elif dep_version == f"^{from_version}":
                            data[dep_type][dep_name] = f"^{to_version}"
                            changed = True
                        elif dep_version == f"~{from_version}":
                            data[dep_type][dep_name] = f"~{to_version}"
                            changed = True

            if changed:
                with open(p_path, 'w', encoding='utf-8') as f:
                    # Try to preserve indentation if possible, usually 2 spaces in these repos
                    json.dump(data, f, indent=2)
                    f.write('\n')
                print(f"Updated {p_path.relative_to(repo_root)}")
                updated_count += 1

        except Exception as e:
            print(f"Error processing {p_path}: {e}")

    print(f"Done! Updated {updated_count} files.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upgrade package versions in a monorepo.")
    parser.add_argument("from_version", help="The current version to upgrade from.")
    parser.add_argument("to_version", help="The new version to upgrade to.")
    parser.add_argument("--root", default=".", help="The root directory of the repository.")

    args = parser.parse_args()
    upgrade_version(args.root, args.from_version, args.to_version)
