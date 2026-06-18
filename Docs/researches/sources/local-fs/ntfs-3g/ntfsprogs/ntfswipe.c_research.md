# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfswipe.c

## Purpose
Implementation of `ntfswipe`, a destructive NTFS sanitation tool that overwrites free clusters, metadata slack, deleted-record remnants, directory index slack, `$LogFile`, and `pagefile.sys`.

## Option Parsing
- `parse_options()` handles short and long options.
- Default operation with no wipe category is `--info`.
- Default replacement byte list is a sentinel-terminated list containing `0`.
- `--bytes` parses comma-separated byte values through `parse_list()`.
- `--count` must be between `1` and `100`.
- `--bytes` and `--undel` are rejected together.
- Quiet/verbose settings are synchronized with NTFS-3G logging levels.

## Main Flow
- `main()` parses options, sets locale, prints summary unless info mode, then mounts the volume.
- Uses read-only mount for `--info` or `--no-action`; write mode otherwise.
- `--force` adds `NTFS_MNT_RECOVER`.
- Refuses dirty volumes unless force is set.
- In write mode without force, gives a 5-second abort window.
- Iterates `opts.count` and each configured replacement byte.
- Dispatches selected wipe operations and totals reported bytes, excluding undelete data.

## Free-Space Wiping
- `wipe_unused()` walks all clusters and writes a full cluster buffer to each cluster not marked in use by `$Bitmap`.
- `wipe_unused_fast()` processes 64-cluster blocks, skips fully used blocks, reads partially free blocks, and skips unused clusters already filled with the target byte.
- The fast path rewrites whole 64-cluster windows after replacing only free clusters in the in-memory block.

## File Tail Wiping
- `wipe_tails()` iterates user MFT records and each `$DATA` attribute.
- `wipe_attr_tail()` opens a named data stream, requires nonresident data, maps the whole runlist, then delegates:
  - `wipe_attribute()` for normal non-compressed data, wiping cluster slack after logical data size.
  - `wipe_compressed_attribute()` for compressed attributes, handling compression-unit holes and residual physical space.
- Encrypted attributes round the effective offset up to 1024-byte units.

## MFT Wiping
- `wipe_mft()` iterates initialized MFT records.
- For in-use records, reads the MFT record with MST fixups and overwrites bytes after `bytes_in_use - 4`.
- For unused records, builds a minimal valid FILE record from scratch.
- Writes both `$MFT` and, when covered, `$MFTMirr`, adjusting the update sequence number before writing the mirror copy.

## Directory Index Wiping
- `wipe_directory()` scans MFT records for nonresident `$INDEX_ALLOCATION` named `$I30`, matching `$BITMAP`, and resident `$INDEX_ROOT`.
- `get_indx_record_size()` reads the index record size from `$INDEX_ROOT`.
- `wipe_index_allocation()` reads the index bitmap:
  - For live INDX records, wipes slack after `index_length`.
  - For unused index records, overwrites the whole record-sized slot.
  - Applies MST fixups before writing live records.

## Special Files
- `wipe_logfile()` overwrites `$LogFile` `$DATA` with `0xff`, regardless of requested byte.
- It first reads the whole logfile to validate readable length before writing.
- `wipe_pagefile()` opens `pagefile.sys` and overwrites its unnamed `$DATA` stream in chunks.

## Undelete Data Wiping
- `wipe_unrm()` scans the MFT bitmap for unused MFT record numbers.
- `destroy_record()` reads each unused record and overwrites:
  - Resident `$FILE_NAME` values and their value lengths.
  - Resident `$DATA` values and lengths.
  - Free clusters referenced by nonresident old runlists, but only if those clusters are still not in use.
  - Nonresident data-size fields in the MFT record.
- Uses `fill_buffer()` to generate repeated shred-like fixed/random patterns. `npasses` derives from byte-list length or count.
- Honors `--no-action` by running logic without writes.

## Dependencies
- Heavy NTFS-3G library use: volume mounting, MFT access, attribute search/open/read/write, runlist handling, cluster bitmap helpers, MST protection, pathname lookup.
- Uses NTFS logging framework for quiet/verbose/error output.

## Safety/Limitations
- Destructive write paths operate directly on metadata and raw clusters.
- `--force` can mount dirty volumes with recovery semantics.
- Several comments are inherited from older ntfsprogs and some operations are explicitly broad-brush.
- `wipe_mft()` info accounting appears to add `bytes_in_use - 4` for live records, while write mode wipes from that point to record end; treat reported info totals as approximate.
- Undelete wiping intentionally mutates deleted MFT records and old metadata remnants, so it is not a recovery-preserving operation.
