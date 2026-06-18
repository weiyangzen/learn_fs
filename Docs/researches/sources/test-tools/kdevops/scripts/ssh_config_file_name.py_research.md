# sources/test-tools/kdevops/scripts/ssh_config_file_name.py

## Purpose
Generates a unique SSH config filename for the current working directory, preventing multiple kdevops checkouts from sharing one generated SSH config.

## Important APIs
`get_directory_hash(path, length=8)` returns the first N hex characters of a SHA256 hash of an absolute path. `generate_ssh_config_filename(base_path="~/.ssh/config_kdevops")` appends the current directory hash to the base path. `main()` handles `--help`, optional custom base path, and default output.

## Control flow and state
The script is pure computation and prints the chosen path. It does not expand `~` or create files.

## Dependencies and integration
Uses Python `hashlib`, `os`, and `sys`. It integrates with provisioning scripts that need a stable `Include ~/.ssh/config_kdevops_*` naming pattern.

## Risks and test signals
Because it hashes `os.getcwd()`, callers must run it from the intended kdevops root. Moving a checkout changes the filename. Test by running from two directories and by passing a custom base path.
