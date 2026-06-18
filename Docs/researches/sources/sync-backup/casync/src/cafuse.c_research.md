# sources/sync-backup/casync/src/cafuse.c

## Purpose
Implements the optional read-only FUSE frontend for casync archives. It mounts a `CaSync` instance as a filesystem and translates FUSE operations into `ca_sync_*` seek, step, metadata, and payload calls.

## Important APIs, Types, and Functions
`ca_fuse_run` mounts and runs the FUSE loop. Static callbacks implement `getattr`, `readlink`, `readdir`, `open`, `read`, `statfs`, `ioctl`, `getxattr`, and `listxattr`. Helpers include `iterate_until_file`, `seek_to_path`, `fill_stat`, `feature_flags_warning`, and a signal handler that forwards quit requests to FUSE.

## Control Flow
FUSE callbacks operate on a single global `CaSync *instance`. Path-based operations seek to the requested path and step until `CA_SYNC_NEXT_FILE`. Reads enable payload mode, seek to path+offset, then copy `CA_SYNC_PAYLOAD` chunks until the requested size or EOF. `readdir` disables payload, seeks to the directory, skips the directory itself, emits child basenames, and uses `ca_sync_seek_next_sibling` to stay at one level. `ca_fuse_run` builds read-only mount options, optionally creates the mountpoint, installs signal handling, warns about unsupported feature flags, notifies readiness, runs `fuse_loop`, then unmounts and destroys state.

## State and Persistence Behavior
The mounted view is transient and read-only. Kernel cache is enabled through FUSE options, while all backing state is fetched from the `CaSync` archive/index/store pipeline. `statfs` derives block count from archive size, not from expanded payload size.

## Dependencies and Integration Points
Requires libfuse API version 26 and Linux ioctls for chattr/FAT attribute exposure. Integrates with `casync-tool.c` when built with `HAVE_FUSE`, with `CaSync` public accessors, notify/signal handling, and format feature utilities.

## Risks
The global `instance`/`fuse` design assumes one mount per process and no concurrent independent sessions. FUSE may issue concurrent callbacks, so mutable `CaSync` seek state is a concurrency-sensitive integration point unless FUSE is effectively single-threaded in this configuration. `fsname=` is noted as needing escaping. Unsupported archive features are only warned about, not blocked.

## Test Signals
Mount/unmount, mkdir-on-demand, signal shutdown, stat/readlink/readdir/read behavior, random read offsets, xattr list/get, chattr and FAT ioctl paths, feature warning output, read-only open rejection for write flags, and archive sources requiring polling are important tests.
