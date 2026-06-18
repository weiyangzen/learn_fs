# sources/object-store/daos/src/vos/storage_estimator/daos_storage_estimator.py

## Purpose
Command-line entry point for the DAOS storage estimator. It exposes subcommands to create sample metadata/YAML, estimate from a live filesystem tree, estimate from existing YAML, or estimate from CSV.

## Important APIs, types, and functions
- `CreateExample.run()` writes VOS metadata and a DFS sample YAML.
- `ProcessFS.run()` explores a path with `FileSystemExplorer`, converts results to YAML, optionally writes it, and prints overhead.
- `ProcessYAML.run()` loads a user YAML file and processes it.
- `process_csv()` delegates to `ProcessCSV`.
- `argparse` subcommands: `create_example`, `explore_fs`, `read_yaml`, and `read_csv`.

## Control flow
The module creates an argparse parser at import/execution time, configures subcommands, parses args, and calls `args.func(args)`. Each wrapper prints the DAOS version, constructs the appropriate processor, runs it, catches exceptions, prints an error, and exits with `-1` on failure.

## State and persistence behavior
State is mostly CLI arguments and generated estimator objects. `create_example` and `explore_fs` can persist YAML/metadata output files. `read_yaml` and `read_csv` are read-only except optional output. The default DAOS storage path is `/mnt/daos`.

## Dependencies and integration points
Integrates `storage_estimator.dfs_sb`, `FileSystemExplorer`, `ProcessCSV`, and utility classes from `storage_estimator.util`. It is the user-facing bridge from DAOS/DFS filesystem observations or CSV summaries to `MetaOverhead`.

## Risks and edge cases
The module assumes a subcommand is provided; otherwise `args.func` is absent. `ProcessFS.run()` and `ProcessYAML.run()` reference the global `args` rather than `self._args`, making reuse harder and tests more coupled to module state. All failures collapse to process exit `-1`, which limits programmatic error handling.

## Test signals
Signals include correct help/subcommand parsing, sample file creation, expected rejection of invalid object classes/EC sizing/checksum names, and stable printed estimates from YAML/CSV/filesystem inputs.
