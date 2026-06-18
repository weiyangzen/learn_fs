# sources/object-store/rustfs/crates/ecstore/src/disks_layout.rs

## Purpose
This file parses RustFS disk/endpoint command-line layouts into erasure pools and sets. It supports both legacy explicit endpoint lists and ellipses-based expansion such as `data{1...64}` or distributed host/disk patterns, then chooses a symmetric supported erasure set size. The result tells later initialization code how many pools, sets, and drives per set exist and which endpoint strings belong to each set.

## Important APIs, types, and functions
`SET_SIZES` lists supported erasure set sizes from 2 through 16. `ENV_RUSTFS_ERASURE_SET_DRIVE_COUNT` optionally forces a specific set drive count.

`PoolDisksLayout` stores the original command-line string for one pool plus a `Vec<Vec<String>>` layout where each inner vector is one erasure set. It exposes `iter`, plus private `new`, `count`, and `get_cmd_line`.

`DisksLayout` stores whether parsing used legacy mode and the list of pools. `DisksLayout::from_volumes` is the public parser. `is_empty_layout`, `is_single_drive_layout`, `get_single_drive_layout`, `get_set_count`, `get_drives_per_set`, and `get_cmd_line` expose parsed topology.

`get_all_sets` is the main conversion helper. It either expands ellipses through `EndpointSet::from_volumes` or builds an `EndpointSet` from explicit args, then rejects duplicate expanded endpoints.

`EndpointSet` holds parsed `ArgPattern`s, expanded endpoint strings, and `set_indexes`. `EndpointSet::from_volumes` parses ellipses, computes total pattern sizes, computes set indexes, expands every pattern into endpoint strings, and returns the set. `EndpointSet::get` slices the flattened endpoint list according to `set_indexes` to produce `Vec<Vec<String>>` sets.

Set-size helpers are `get_divisible_size`, `possible_set_counts`, `is_valid_set_size`, `common_set_drive_count`, `possible_set_counts_with_symmetry`, `get_set_indexes`, and `get_total_sizes`.

## Control flow
`DisksLayout::from_volumes` rejects empty input, detects whether any argument has ellipses, reads `RUSTFS_ERASURE_SET_DRIVE_COUNT` with default `"0"`, and parses it as `usize`. Without ellipses it treats all args as one legacy pool and calls `get_all_sets` with all endpoints. With ellipses it requires all args to have ellipses when multiple args are supplied, then parses each argument as a separate pool.

`get_all_sets` constructs an `EndpointSet`, calls `get` to build set vectors, then scans every endpoint string with a `HashSet` to reject duplicates. For non-ellipses multi-arg input, `get_set_indexes` is called with total size equal to the number of explicit args. A single explicit endpoint becomes one set of one drive.

For ellipses, `EndpointSet::from_volumes` calls `find_ellipses_patterns` for each argument, computes each argument's total expansion size, calls `get_set_indexes`, expands all patterns, and flattens expansions into the endpoint list. `EndpointSet::get` then walks `set_indexes`, slicing consecutive endpoints into sets.

`get_set_indexes` validates each total size against minimum supported set size and the forced set count. It computes the greatest common divisor of all total sizes, filters supported set sizes that divide that common size, filters again for symmetry against each ellipses pattern, then either accepts the forced set-drive count or chooses `common_set_drive_count`. Finally it maps each total size to repeated `set_size` entries.

## State and persistence behavior
No filesystem or persistent state is written. The only external state read is `RUSTFS_ERASURE_SET_DRIVE_COUNT`, which can force layout selection or cause parsing to fail if incompatible with the endpoint count and symmetry constraints. Parsed layout state is held in `DisksLayout`/`PoolDisksLayout` values and consumed by store initialization.

## Dependencies and integration points
The parser depends on `rustfs_utils::string::{has_ellipses, find_ellipses_patterns, ArgPattern}` for ellipses parsing/expansion, `serde::Deserialize` for config deserialization, `std::env`, `std::io::Error/Result`, `HashSet`, and tracing `debug` for environment default logging. It feeds endpoint topology into the erasure store initialization path and must remain compatible with endpoint parsing in `disk::endpoint`.

## Risks and edge cases
The forced set-drive-count environment variable is parsed directly and any non-numeric value fails layout parsing. That is useful for surfacing misconfiguration but can make startup sensitive to environment drift.

The single-drive explicit layout bypasses normal erasure minimums by returning `vec![vec![args.len()]]` when only one arg is provided. Callers must distinguish single-drive mode from erasure-coded multi-drive mode.

`possible_set_counts_with_symmetry` mutates a `symmetry` flag while iterating patterns; for complex multi-pattern arguments, the final value for each candidate can depend on the last checked pattern element. The test matrix covers many representative cases, but symmetry logic is subtle and startup-critical.

Duplicate detection happens after expansion, so very large ellipses inputs allocate all endpoints before discovering duplicates. Error messages use `std::io::Error::other`, which loses structured error kinds.

Changing `SET_SIZES` or `common_set_drive_count` selection changes the physical erasure layout derived from the same command line. That is a compatibility-sensitive startup behavior.

## Test signals
Tests cover greatest common divisor calculation, many `get_set_indexes` layouts including invalid too-large/unsupported cases, host/disk/rack ellipses, Kubernetes-style zero-based ranges, padded numeric ranges, more than two ellipses, standalone multi-ellipsis paths, and invalid pattern forms. The expected indexes assert the selected erasure set size and number of sets for each topology.
