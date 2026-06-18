# sources/security-integrity/cryfs/crates/cryfs-runner/src/runner.rs

## Purpose
Assembles blockstore, blobstore, CryFS device, unmount triggers, and RustFS/FUSE backend into the actual mount lifecycle.

## Important APIs, types, and functions
- `Backend` aliases the fuser RustFS backend.
- `CreateOrLoad`, `MountArgs`, and `FuseOption` are serialized mount configuration types.
- `mount_filesystem` sets integrity behavior, blockstore stack, unmount trigger, device, and backend mount.
- `FilesystemRunner` implements `BlockstoreCallback`.
- `make_device` parses root blob id, creates or loads `CryDevice`, and runs `sanity_check`.

## Control flow
`mount_filesystem` derives missing-block integrity policy, installs an integrity-violation callback that triggers unmount, then runs `setup_blockstore_stack` with a callback. The callback builds `BlobStoreOnBlocks`, creates/loads and validates a `CryDevice`, optionally starts idle-unmount polling, converts atime and FUSE ACL options into RustFS config, mounts the backend, and waits for unmount. After return, trigger reason determines whether success, idle unmount success, or integrity violation error is reported.

## State and persistence behavior
Persistent state includes on-disk blocks under the vault dir, local-state locking/integrity metadata, blobstore content, root directory blob, and filesystem mutations performed through the mounted device. Runtime state includes `UnmountTrigger`, last access timestamp, mount options, and client id.

## Dependencies and integration points
Uses `OnDiskBlockStore`, `LockingBlockStore`, `BlobStoreOnBlocks`, `CryConfig`, `LocalStateDir`, `CryDevice`, `cryfs_rustfs` backend/config/session ACL, CLI error mapping, and `UnmountTrigger`.

## Risks and edge cases
`make_device` drops the blobstore on invalid root blob id and drops the device after failed sanity check. `logical_block_size` conversion in lower device statfs can unwrap if oversized. ACL mapping collapses allow-other/root into a single fuser `SessionACL`. Integrity violations asynchronously trigger unmount, so error reporting depends on trigger reason surviving until mount returns.

## Test signals
There is a TODO for tests. Expected coverage includes create vs load, invalid root id, failed sanity check cleanup, mount option mapping, allow-other/root precedence, idle unmount, integrity violation unmount, and missing-block policy behavior.
