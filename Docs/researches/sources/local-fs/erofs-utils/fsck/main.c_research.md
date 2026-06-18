# File Research: sources/local-fs/erofs-utils/fsck/main.c

## Purpose
Implements `fsck.erofs`, including image opening, superblock verification, inode traversal, xattr validation/dumping, optional decompression verification, extraction to a host directory, hardlink preservation, packed-fragment verification, compression-ratio accounting, and fuzzing entry points.

## Main Structures
- `struct erofsfsck_cfg`: global fsck state, including traversal stack, extract path, counters, options, target nid/path, and corruption flag.
- `struct erofsfsck_dirstack`: recursion/loop guard for directory traversal.
- `struct erofsfsck_hardlink_entry`: extraction-time nid-to-path table for non-directory hardlinks.
- `struct erofsfsck_get_parent_ctx`: helper context for resolving `..` when checking a non-root directory.

## Important Functions
- `erofsfsck_parse_options_cfg()`: parses CLI options such as `--extract`, `--device`, `--offset`, `--nid`, `--path`, `--xattrs`, `--no-sbcrc`, preserve flags, and verbosity.
- `erofs_verify_xattr()`: validates inode xattr ibody layout and entry boundaries.
- `erofsfsck_dump_xattrs()`: lists and optionally restores xattrs during extraction, with non-root handling for non-user namespaces.
- `erofs_verify_inode_data()`: maps every file extent, validates lengths, optionally decompresses/reads data, writes extraction output, and counts logical/physical blocks.
- `erofs_extract_dir()`, `erofs_extract_file()`, `erofs_extract_symlink()`, `erofs_extract_special()`: extraction handlers by inode type.
- `erofsfsck_dirent_iter()`: directory callback that extends the current path and recurses into `erofsfsck_check_inode()`.
- `erofsfsck_check_inode()`: central recursive verifier for one inode.
- `main()` / `erofsfsck_fuzz_one()`: initialize config, open devices, read superblock, initialize packed file if needed, choose target inode, run verification, and clean up.
- `LLVMFuzzerTestOneInput()`: writes fuzzer input to a temp file and invokes the fuzzing main path.

## Behavior
- Extraction with `--extract=X` implies decompression/data verification and writes files under a bounded `PATH_MAX` buffer.
- Extraction to `/` is blocked unless `--force` is present.
- `--overwrite` may remove/retry existing files or directories, but uses `O_NOFOLLOW` for regular-file creation.
- Packed fragment inode is verified before the root tree when fragments are enabled.
- Directory traversal checks for loops, `.`/`..` correctness, and path length.
- Non-I/O verification failures set `fsckcfg.corrupted`; final exit status is `1` on any error/corruption.

## Interactions
- Uses `erofs_read_superblock`, `erofs_read_inode_from_disk`, `erofs_map_blocks`, `z_erofs_read_one_data`, `erofs_read_one_data`, `erofs_iterate_dir`, `erofs_iopen`, xattr helpers, blob-device helpers, and packed-file helpers.
- Lists available compressors via `z_erofs_list_available_compressors()` from the compressor registry.

## Notes
The file combines verification and extraction. Most corruption findings return negative errno-style values internally but convert to process exit code `1`.
