# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfsundelete.c

## File Role

`ntfsundelete.c` implements the `ntfsundelete` command. It mounts an NTFS volume read-only, scans deleted MFT records, estimates recoverability from the allocation bitmap, and writes recovered data streams to files outside the NTFS volume.

It supports:

- scanning deleted records
- undeleting by inode range
- undeleting by filename pattern
- copying raw MFT record ranges
- filtering by name, size, modification time, and recoverability
- filling unrecoverable regions with a configured byte
- optional optimistic recovery from clusters currently marked in use

## Major Dependencies

The file uses:

- `ntfsundelete.h` for option and recovered-file structs
- `bootsect.h`, `mft.h`, `attrib.h`, `layout.h`, `inode.h`, and `device.h`
- `ntfs_attr_open`, `ntfs_attr_pread`, `ntfs_attr_mst_pread`, `ntfs_attr_close`
- `ntfs_mapping_pairs_decompress`
- `utils_mount_volume`, `utils_cluster_in_use`, `utils_parse_range`
- `ntfs_cluster_read`
- `ntfs_ucstombs`, `ntfs_mbstoucs`
- `ntfs2timespec`
- optional system regex; if absent, an internal wildcard matcher over NTFS Unicode names is compiled

The Makefile builds it from `ntfsundelete.c`, `ntfsundelete.h`, `utils.c`, `utils.h`, and `list.h`.

## Option Parsing

`parse_options()` accepts both short and long options. It enforces a single mode among scan, undelete, and copy. If no mode is selected, scan is default.

Important parsing behavior:

- `--inodes` is parsed by `parse_inode_arg()` into inclusive ranges.
- `--match` is transformed from shell-style wildcards into anchored regex when regex support exists.
- `--time` converts values such as days/weeks/months/years ago into an absolute `time_t`.
- scan rejects output/destination/truncate/fill-byte options.
- copy rejects recovery and scan filters.
- quiet cannot be combined with verbose or scan.
- `--parent` requires verbose mode.

The global `ranges`, `nr_entries`, `with_regex`, and `avoid_duplicate_printing` variables coordinate undelete selection.

## MFT Record Reading

`read_record()` reads a single MFT record from `$MFT/$DATA` using MST-aware reads, builds a `struct ufile`, and gathers:

- standard-information last data change time
- attribute-list presence
- directory status from `$INDEX_ROOT`
- filename attributes through `get_filenames()`
- data streams through `get_data()`

It temporarily disables perror logging while inspecting suspicious deleted records.

`get_filenames()` walks `$FILE_NAME` attributes, converts names to the current locale, tracks parent references when requested, picks a preferred name by lowest namespace value, and updates the maximum seen size. If no filename exists, `rescue_name()` tries to recover a stale name from unused MFT-record space for simple unfragmented cases.

`get_parent_name()` reads the parent MFT record and `verify_parent()` checks it is plausibly the parent directory before using its filename.

`get_data()` walks `$DATA` attributes, records stream names, residency, compression/encryption flags, sizes, resident data pointers, and decompressed runlists.

## Recoverability Calculation

`calc_percentage()` estimates recovery by walking each data stream:

- directories return 0%
- resident data returns 100%
- encrypted and compressed streams are treated as unrecoverable
- unmapped runlist segments count as in-use/unrecoverable
- sparse holes count as recoverable zeroes
- normal LCN runs are checked cluster-by-cluster with `utils_cluster_in_use()`

The best percentage across data streams is returned and stored per stream for display and truncation decisions.

This is only a potential-recovery estimate; the implementation cannot prove that free clusters still contain the old data.

## Scan Mode

`scan_disk()` opens `$MFT/$BITMAP`, iterates bits for records not in use, reads each deleted record, applies filters, calculates recoverability, and prints either one-line summaries or verbose dumps.

Filters include:

- modification time after `opts.since`
- filename regex/pattern match
- size range
- minimum recoverability percentage

If scan is being used as undelete-by-regex, matching records are passed to `undelete_file()` after display, with duplicate printing suppressed.

## Undelete Mode

`handle_undelete()` requires either inode ranges or a match regex. With regex it scans and recovers matches; with inode ranges it loops over every inode in every range and calls `undelete_file()`.

`undelete_file()`:

1. Reads the MFT record.
2. Optionally displays file info.
3. Rejects records still in use unless forced.
4. Calculates recoverability and skips records with 0%.
5. For each data stream, creates a host output pathname from destination, chosen filename, and optional stream name.
6. Writes resident data directly.
7. For nonresident data, walks runlists:
   - unmapped segments are filled with `opts.fillbyte`
   - sparse holes are written as zeroes
   - in-use clusters are filled unless `--optimistic` is set
   - free/optimistic clusters are read from the NTFS volume with `ntfs_cluster_read()`
8. Applies `--truncate` only for fully recoverable, internally consistent nonresident streams.
9. Sets the host output file timestamp to the recovered last-data-change time.

Named NTFS streams are written as `filename:stream`.

## Copy Mode

`copy_mft()` writes a requested MFT record range into a host file. It clamps the end of the range to the volume’s initialized MFT record count, reads `$MFT/$DATA`, and writes fixed-size records to `opts.output` or default `mft`.

## Output and Diagnostics

`list_record()` produces the compact scan table. `dump_record()` prints detailed file, filename, date, flag, stream, runlist, and recoverability data. Logging is routed through ntfs-3g logging APIs, with quiet/verbose settings parsed into `opts`.

## Main Flow

`main()` initializes logging, parses options, sets locale, mounts the volume read-only with optional `NTFS_MNT_RECOVER` under `--force`, dispatches the selected mode, unmounts, frees match regex text, and returns the mode result.

## Notable Risks and Limitations

- The NTFS volume is mounted read-only; recovered data is written only to host files.
- Multi-record attribute-list cases are flagged, but data from missing/extended records is not reconstructed.
- Compressed and encrypted streams are not recovered.
- Recovery trusts deleted MFT metadata that may be stale, inconsistent, or reused.
- Output path buffers are fixed-size 256-byte arrays in recovery/copy paths, so long destination/name combinations may be truncated by `snprintf()`.
- `write_data()` handles one partial write retry; callers detect short writes as failure.
