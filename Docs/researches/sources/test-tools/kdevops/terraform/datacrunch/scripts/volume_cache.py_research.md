# sources/test-tools/kdevops/terraform/datacrunch/scripts/volume_cache.py

## Purpose
This Python CLI manages DataCrunch OS-NVMe volume ID mappings for faster reprovisioning. It stores per-host mappings keyed by kdevops host prefix.

## Important APIs, Types, And Functions
`get_cache_dir()` creates `~/.cache/kdevops/datacrunch`. `get_cache_file(prefix)` returns `<prefix>.yml`. `load_cache()` reads YAML and returns `{}` on missing file or read/parse error. `save_cache()` writes YAML. Command handlers `cmd_save`, `cmd_load`, `cmd_delete`, `cmd_list`, and `cmd_clear` implement the CLI subcommands. `main()` builds an argparse subcommand parser requiring `command`.

## Control Flow
Each subcommand loads or modifies one prefix file. `save` upserts a hostname-volume mapping. `load` prints the volume ID or exits 1. `delete` removes a hostname if present. `list` prints all mappings. `clear` unlinks the entire prefix file. The process exits with the handler's status.

## State And Persistence
Persistent state is YAML files under the user's home cache directory. Writes are direct and not atomic. There is no locking, so concurrent apply/destroy/cache operations can race.

## Dependencies And Integration Points
It depends on PyYAML and Python standard `argparse`, `pathlib`, `os`, and `sys`. It is invoked by DataCrunch apply/destroy wrappers and can be used manually for troubleshooting cache state.

## Risks And Test Signals
Direct YAML writes can corrupt cache files if interrupted. Prefix and hostname are accepted without validation, so unusual strings can create surprising filenames or mappings. Load errors are swallowed into empty cache, which can overwrite bad data on the next save. Tests should use a temporary HOME, exercise all subcommands, simulate invalid YAML, verify exit codes, and test concurrent write behavior if wrappers can run in parallel.
