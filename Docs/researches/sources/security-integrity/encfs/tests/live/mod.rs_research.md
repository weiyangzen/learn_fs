# sources/security-integrity/encfs/tests/live/mod.rs

Purpose: shared harness for ignored live FUSE tests. It gates live execution, creates temporary backing/mount directories, loads fixture config metadata, mounts the `encfs` binary, and cleans up.

Important APIs/types/functions: `LIVE_ENV`, `LiveConfig`, `LiveConfigKind`, `live_lock`, `live_enabled`, `manifest_dir`, `fixtures_dir`, `load_live_config`, `data_block_size`, `unique_temp_dir`, `path_has_tool`, `MountGuard::mount`, `MountGuard::mount_existing_backing_root`, `init_backing_root`, `list_non_dot_entries_recursive`, and `backing_single_ciphertext_file`.

Control flow: `MountGuard` checks `ENCFS_LIVE_TESTS`, serializes with a global mutex, copies the selected fixture to a backing root, spawns `encfs -f -S` with optional `-r`, writes the password to stdin, drains stdout/stderr into bounded tails, polls `/proc/self/mountinfo`, and unmounts via `fusermount3`, `fusermount`, or `umount` on drop.

State and persistence: creates temp directories using pid/time/counter; may preserve externally supplied backing roots until caller cleanup; holds child process state and mount status in the guard.

Dependencies and integration points: depends on Cargo `encfs` binary, Linux mountinfo, FUSE/unmount tools, fixture configs, `EncfsConfig`, and Unix paths.

Risks: Linux-specific mount detection; live tests can hang or fail under restricted CI. `init_backing_root` copies all fixture kinds to `.encfs6.xml`, so V7 behavior depends on consumers setting kind/path correctly. Cleanup is best-effort.

Test signals: enables the live suites to validate actual kernel/FUSE behavior rather than only direct trait calls.
