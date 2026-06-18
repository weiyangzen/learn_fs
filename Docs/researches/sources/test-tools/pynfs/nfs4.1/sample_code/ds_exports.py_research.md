# sources/test-tools/pynfs/nfs4.1/sample_code/ds_exports.py

## Purpose
`ds_exports.py` is a minimal exports module for running a files-layout pNFS data server. It defines the `mount_stuff(server, opts)` hook consumed by `nfs4server.read_exports`.

## Important APIs, Types, and Functions
- `mount_stuff(server, opts)` creates a `StubFS_Mem(2)` filesystem and mounts it on `/pynfs_mds`.

## Control Flow
When the server starts with `--exports ds_exports.py`, `read_exports` imports this module and invokes `mount_stuff`. The function constructs the memory-backed stub filesystem and calls `server.mount`.

## State and Persistence Behavior
State is in memory through `StubFS_Mem`; there is no on-disk persistence in this sample. The numeric argument `2` is passed to the filesystem constructor and likely controls the sample filesystem identity or layout behavior.

## Dependencies and Integration Points
The file imports `StubFS_Mem` from `fs` and depends on the server exposing `mount(fs, path)`. It pairs with `dataservers.conf` and files-layout pNFS sample runs.

## Risks and Edge Cases
The mount path must match the MDS expectation in sample data-server configuration. Because the backing filesystem is memory-only, server restarts lose contents and state. There is no option handling despite receiving `opts`.

## Test Signals
A successful server startup with this exports file should log or print the mount and expose `/pynfs_mds`. pNFS file-layout tests can then validate data-server access through the mounted stub.
