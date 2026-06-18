# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/filesystem_driver/mounting.rs

## Purpose
Benchmark-only `FilesystemDriver` implementation that mounts CryFS into a temp directory through fuser or fuse-mt backends and performs real OS syscalls.

## Important APIs, types, and functions
- `MountingBackend` with `spawn_mount`.
- `FuserBackend` and `FusemtBackend`.
- `MountingFilesystemDriver<B>` with `MaybeMounted` state.
- Helpers `real_path_for_node`, `metadata_to_node_attrs`, `asyncify`, and `to_timespec`.

## Control flow
`new` stores an unmounted device and temp mount directory. `init` swaps state from `NotMounted` to `Mounted` by spawning the selected backend. `destroy` swaps back through `Invalid` and unmounts in a blocking task. Filesystem operations translate abstract absolute paths to paths under the mount directory and call Tokio fs APIs, libc/nix functions, or file-handle methods.

## State and persistence behavior
State is a mutex-protected mount lifecycle enum. Filesystem contents persist in the underlying fixture stores while mounted. Temp mount directory is removed when `TempDir` drops. Reset-cache hooks are no-ops because real kernel/OS caches are outside the in-process harness.

## Dependencies and integration points
Integrates `cryfs_rustfs` mounted backends, `fuser`, `tokio::fs`, Unix metadata and permission APIs, `nix`, and the generic fixture. It is used only with the `benchmark` feature.

## Risks and edge cases
The file uses small `unsafe` libc calls for chmod despite the crypto crate forbidding unsafe elsewhere. OS/kernel behavior can add extra filesystem activity, so this driver is unsuitable for deterministic operation counts. Mutex state panics on invalid lifecycle calls.

## Test signals
Criterion benchmark behavior under mounted fuser/fuse-mt drivers; functional failures surface as `FsError::InternalError` or assertions in read/write sizing.
