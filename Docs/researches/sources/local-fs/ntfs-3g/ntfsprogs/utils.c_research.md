# File Research: sources/local-fs/ntfs-3g/ntfsprogs/utils.c

## Purpose

Shared utility implementation for NTFS command-line tools. It wraps libntfs-3g behaviors with ntfsprogs-compatible helpers for locale setup, device validation, volume mounting diagnostics, size/range parsing, attribute lookup, pathname reconstruction, allocation bitmap checks, metadata classification, memory dumping, and MFT iteration.

## Main Responsibilities

- Provides user-facing diagnostic text for invalid, corrupt, hibernated, busy, dirty, journal-unclean, and FakeRAID-like NTFS mount failures.
- Validates a target device/path before tool use, including existence and mounted-state checks unless forced.
- Mounts NTFS volumes with ntfsprogs-style safety behavior over libntfs-3g.
- Parses numeric size and range arguments with optional decimal suffix scaling.
- Searches raw MFT records and inode-backed records for NTFS attributes.
- Reconstructs an inode path by walking parent `FILE_NAME` attributes up to `$Root`.
- Maps NTFS attribute records to printable attribute type/name strings.
- Tests cluster and MFT-record allocation status through cached reads of `$Bitmap` and `$MFT/$BITMAP`.
- Identifies NTFS metadata files by MFT number, base record, and parent metadata location.
- Iterates MFT records according to filter flags such as in-use, file, directory, metadata, and base-record state.
- Supplies Windows-specific printf format/path compatibility helpers when built with `HAVE_WINDOWS_H`.

## Key Functions

- `utils_set_locale()` calls `setlocale(LC_ALL, "")`; logs and keeps the default locale if unavailable.
- `ntfs_mbstoucs_libntfscompat()` emulates linux-ntfs `ntfs_mbstoucs()` semantics, including support for caller-provided output buffers.
- `utils_valid_device()` checks null input, `stat()`, and mounted state through `ntfs_check_if_mounted()`.
- `utils_mount_volume()` validates then calls `ntfs_mount()`, translating common `errno` values into specific operator guidance; also rejects dirty volumes unless `NTFS_MNT_RECOVER` is present.
- `utils_parse_size()` uses `strtoll()` and accepts decimal `K/M/G/T` suffixes when `scale` is true.
- `utils_parse_range()` parses `start-finish`, defaulting missing start to `0` and missing finish to `LONG_MAX`.
- `find_attribute()` and `find_first_attribute()` wrap `ntfs_attr_lookup()` with search context allocation/cleanup.
- `utils_inode_get_name()` walks `AT_FILE_NAME` parent references, converts UCS names to locale strings, and assembles a slash-separated path.
- `utils_attr_get_name()` converts attribute definition names and optional named-stream names into a caller buffer.
- `utils_cluster_in_use()` and `utils_mftrec_in_use()` use static 512-byte bitmap caches to avoid repeated small bitmap reads.
- `utils_is_metadata()` classifies core NTFS metadata and children of metadata files.
- `utils_dump_mem()` logs formatted hex/ascii memory dumps with optional color/indent flags.
- `mft_get_search_ctx()`, `mft_put_search_ctx()`, and `mft_next_record()` implement a reusable MFT scanner over allocated and unallocated records.
- `ntfs_utils_reformat()` rewrites `%ll*` printf formats to `%I64*` for older Windows C runtimes.
- `ntfs_utils_unix_path()` duplicates a path and converts `\` to `/`.

## Important Details and Edge Cases

- `utils_parse_size()` checks `errno == ERANGE` but does not clear `errno` before `strtoll()`, so callers relying on stale `errno` behavior should be cautious.
- Size suffix scaling is decimal thousands, not binary powers.
- `utils_inode_get_name()` caps parent walking at 20 path elements and may report overly deep directory structures.
- `utils_inode_get_name()` closes parent inodes it opens but deliberately does not close the original inode.
- `utils_attr_get_name()` returns `0` both for unnamed attributes after writing the type and for several error/truncation paths; callers cannot treat `0` as a simple failure without considering side effects.
- Bitmap allocation helpers use static caches and are not thread-local.
- `mft_next_record()` can synthesize an `ntfs_inode` for unused MFT records by reading raw `$MFT/$DATA`.
- `mft_next_record()` marks records as base/non-base using the presence of standard information and attribute list attributes, then optionally detects directories through `$I30` index roots.
- Dirty-volume handling is intentionally different from older libntfs behavior: libntfs-3g is considered capable of handling the dirty bit, but this wrapper still rejects it unless recover/force semantics are requested.

## Dependencies

- Internal NTFS headers: `utils.h`, `types.h`, `volume.h`, `debug.h`, `dir.h`, `logging.h`, `misc.h`.
- libntfs-3g operations: mount/unmount, inode open/close, attribute search/open/read, MFT record read, bitmap access, Unicode conversion.
- Platform headers selected through `config.h` feature macros.

## Role in Source Tree

This file is support infrastructure for `ntfsprogs` utilities. It is not the FUSE driver itself; it gives standalone NTFS utilities consistent parsing, traversal, mount validation, diagnostics, and record-scanning helpers.
