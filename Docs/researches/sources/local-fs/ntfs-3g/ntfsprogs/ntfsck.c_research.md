# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfsck.c

## Role

`ntfsck.c` is an early/preliminary NTFS consistency checker. It can open an NTFS device read-only, verify basic boot-sector structure, bootstrap enough metadata to load `$MFT` and `$MFT/$BITMAP`, mount the volume read-only, and perform low-level MFT record and attribute sanity checks. Full repair and comprehensive volume checking are explicitly unfinished.

## Return Codes

The file defines fsck-style return bits for corrected errors, reboot needed, uncorrected errors, operational errors, syntax errors, cancellation, and shared-library errors. In practice, `main()` currently returns simple nonzero statuses based on errors or unsupported paths.

## Global State

- `errors` and `unsupported` count findings and unimplemented checks.
- `bytes_per_sector`, `sectors_per_cluster`, and `current_mft_record` track check context.
- `mft_rl` and `mft_bitmap_rl` hold preliminary runlists.
- `mft_bitmap_records` and `mft_bitmap_buf` hold the loaded `$MFT/$BITMAP`.

## Boot And Metadata Bootstrap

- `verify_boot_sector()` reads the first 512 bytes, checks the x86 jump pattern, NTFS OEM magic, bytes-per-sector sanity, and parses the boot sector into a preliminary `ntfs_volume`.
- `load_runlist()` reads a file record from a byte offset, walks attribute records with minimal defensive checks, and returns a decompressed runlist for the requested attribute type.
- `verify_mft_preliminary()` loads `$MFT/$DATA` and `$MFT/$BITMAP` runlists from `$MFT`, falling back to `$MFTMirr`, then loads the MFT bitmap.
- `mft_bitmap_load()` reads the bitmap through `ntfs_rl_pread()`, and `mft_bitmap_get_bit()` tests whether a record is allocated.

## Record Checking

- `check_file_record()` validates `FILE` magic, update sequence array bounds, attribute area bounds, record flags, USA fixups, and then iterates attributes.
- `check_attr_record()` checks attribute overflow, type range, minimum length, first-attribute expectations, flags, resident/non-resident mode, resident value bounds, resident flags, and reserved fields. Many deeper semantic checks are left as TODO comments.
- `verify_mft_record()` skips bitmap-free records, reads allocated records through `$MFT`, and calls `check_file_record()`.
- `check_volume()` is marked unsupported but still iterates initialized MFT records and calls `verify_mft_record()`.

## Main Flow

`main()` accepts exactly one device argument, opens it read-only with default ntfs device I/O, verifies the boot sector, performs preliminary MFT bootstrap, closes the raw device, mounts the volume read-only through `ntfs_device_mount()`, calls unsupported log replay and volume checking stubs, reports counters, possibly resets the dirty flag if nothing was found, unmounts, and returns status.

## Important Limitations And Bugs

- The large command-line TODO block shows intended fsck features, but only the single-device positional form is implemented.
- `replay_log()` and `check_volume()` both mark unsupported, so clean volumes can still produce unsupported status.
- The checker is read-only and does not actually repair structures.
- `verify_mft_preliminary()` ends with a FIXME return value after loading the bitmap, indicating incomplete control-flow design.
- `reset_dirty()` uses `if (!(vol->flags | VOLUME_IS_DIRTY))`, which tests a bitwise OR rather than whether the dirty bit is set; that condition is effectively wrong for normal flag values.
- Several error paths leak buffers or runlists, which is less severe for a short-lived checker but important if reused as a library routine.

## Dependencies

The file uses ntfs-3g device I/O, boot-sector parsing, mapping-pair decompression, runlist reads, bit operations, MFT/attribute layout definitions, mounting, logging, and volume flag writes.
