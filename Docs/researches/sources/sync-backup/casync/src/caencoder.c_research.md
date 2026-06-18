# sources/sync-backup/casync/src/caencoder.c

## Purpose
Implements `CaEncoder`, the streaming archive encoder for casync. It walks a base regular file, block device, or directory tree and emits the casync archive format defined in `caformat.h`: `ENTRY` metadata records, optional metadata subrecords, file payload bytes, directory `FILENAME` records, and directory `GOODBYE` lookup tables. It also exposes current-file metadata, seekable `CaLocation` checkpoints, and optional archive/payload/hardlink digests.

## Important APIs, Types, and Functions
The public lifecycle is `ca_encoder_new`, `ca_encoder_unref`, `ca_encoder_set_base_fd`, `ca_encoder_step`, and `ca_encoder_get_data`. `CaEncoderState` drives the stream: `INIT`, `ENTERED`, `ENTRY`, `IN_PAYLOAD`, directory entry states, `GOODBYE`, `FINALIZE`, and `EOF`. `CaEncoderNode` caches the current stack of filesystem nodes, including fds, stat data, sorted dirents, symlink targets, xattrs, ACLs, capabilities, btrfs flags, SELinux labels, quota project IDs, mount IDs, and `CaNameTable` state. Metadata accessors such as `ca_encoder_current_mode`, `ca_encoder_current_xattr`, `ca_encoder_current_location`, and digest getters mirror the current state.

## Control Flow
`ca_encoder_set_base_fd` validates and seeds the root node. Each `ca_encoder_step` advances buffered/skipped byte accounting and dispatches to `ca_encoder_step_node`. Naked top-level regular files or block devices go straight to payload streaming; directory trees begin with an `ENTRY`. For directories, sorted `scandirat` output creates deterministic traversal, `.caexclude`, nodump, submount, unsupported type, and virtual filesystem filters decide whether children are serialized, then each child is preceded by a `FILENAME` record. Directory finalization emits a BST-ordered `GOODBYE` table derived from name-table offsets.

`ca_encoder_get_data` materializes bytes for the state reported by `step`: metadata in `ca_encoder_get_entry_data`, payload via `pread`, filename records, or goodbye tables. If the caller requests no data and no digest needs payload bytes, the encoder can skip payload ranges while still advancing offsets.

## State and Persistence Behavior
Encoder state is in memory, but it serializes stable on-disk archive records. `archive_offset`, `payload_offset`, `skipped_bytes`, node-stack indexes, and per-node caches determine resumability. `ca_encoder_current_location` records relative path, designator, stream offset, stat freshness markers, feature flags, archive offset, and optional name-table chains. `ca_encoder_seek_location` reconstructs node stack state from that location and deliberately invalidates digest/name-table guarantees when resuming mid-object. UID/GID shifting and feature flags alter emitted metadata, so cached locations include feature flags.

## Dependencies and Integration Points
Depends on Linux/POSIX filesystem APIs, ACL, xattr, SELinux when enabled, btrfs ioctls, FAT and chattr flags, quota project ID helpers, `CaMatch` exclude matching, `CaNameTable`, `CaLocation`, `CaDigest`, and `ReallocBuffer`. It is consumed by higher-level sync/archive code and must match decoder expectations for `caformat.h`.

## Risks
High-risk areas are traversal determinism, race handling while files change, Linux-specific metadata fallbacks, and offset accounting across skipped payloads. `GOODBYE` generation requires valid archive offsets and name tables, so seeks can produce `-ENOLINK`. ACL/xattr/capability serialization has variable-sized unaligned records. Digest APIs are state-sensitive: archive digest is only final at EOF, payload/hardlink digests only at finalize and can be stale after partial seeks.

## Test Signals
Test regular-file naked archives, directory trees with sorted entries, empty dirs, symlinks, devices, FIFOs/sockets gating, block-device sizing, xattrs, file capabilities, ACLs, SELinux labels, chattr/FAT flags, btrfs subvolumes, project quotas, `.caexclude`, nodump, submount exclusion, seek/resume from all location designators, digest validity after full and partial reads, and archive equality against decoder round trips.
