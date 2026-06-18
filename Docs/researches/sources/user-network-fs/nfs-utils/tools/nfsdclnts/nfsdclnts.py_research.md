<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/nfsdclnts/nfsdclnts.py -->
# sources/user-network-fs/nfs-utils/tools/nfsdclnts/nfsdclnts.py

## Purpose

`nfsdclnts.py` reads NFS server client state exported under `/proc/fs/nfsd/clients` and prints a tabular view of NFSv4 opens, delegations, locks, and layouts, optionally including client identity details.

## Important APIs, Types, and Functions

`file_to_dict` parses colon-separated `info` files. `getpaths` enumerates each client's `states` file. `opener` YAML-loads a `states` file and appends the matching `info` path. `printer` combines state YAML and client info into formatted rows. `print_cols` renders headers based on requested state type and client fields. `nfsd4_show` owns argparse setup, multiprocessing, signal handling, and output orchestration.

## Control Flow

The CLI accepts a type filter, optional explicit files, hostname/client-info display choices, verbosity, and quiet mode. It chooses explicit `--file` paths or discovers `/proc/fs/nfsd/clients/*/states`, uses a multiprocessing pool to parse YAML in parallel, filters out failed parses, prints headers unless quiet, and prints rows for matching object types.

## State and Persistence Behavior

The script is read-only. State exists only as parsed YAML/list/dict objects in worker and parent processes. The authoritative runtime source is procfs state exported by the kernel NFS server.

## Dependencies and Integration Points

It depends on Python multiprocessing, signals, `PyYAML`, `/proc/fs/nfsd/clients`, and the kernel's `states` YAML-like format and `info` files. It is an admin diagnostic tool for nfsd state rather than a control path.

## Risks and Edge Cases

`verbose` is a global used by helpers. YAML is loaded with `BaseLoader`, so all values are strings, matching display needs but not typed validation. Many broad `except` blocks hide malformed state unless verbose. `getpaths` has indentation irregularities but valid Python in this file. `printer` mutates its `data_list` by popping the info path. Output column width truncates long hostnames but not filenames. Multiprocessing can be expensive for small client sets.

## Test Signals

Fixture tests should cover procfs discovery failure, empty clients, explicit file mode, malformed YAML, missing info keys, all state types, quiet header suppression, hostname truncation, clientinfo columns, and interrupt handling that terminates workers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/nfsdclnts/nfsdclnts.py -->
