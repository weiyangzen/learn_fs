# File Research: sources/local-fs/e2fsprogs/misc/mke2fs.c

`mke2fs.c` is the main implementation of the `mke2fs`/`mkfs.ext*` formatter. It parses command-line and profile configuration, derives filesystem parameters, validates feature combinations and device constraints, then constructs ext2/ext3/ext4 filesystem metadata through libext2fs.

Global role:
- Owns process-wide formatting state used by helper modules, including `program_name`, `quiet`, `verbose`, `fs_types`, and `zero_hugefile`.
- Exports profile lookup helpers declared in `mke2fs.h` and used by `mk_hugefiles.c`.
- Integrates device probing, bad-block handling, undo files, discard, journaling, quota inodes, orphan file creation, root population, and final filesystem close/writeout.

Primary phases:

1. Early setup and option parsing via `PRS()`
- Initializes profile config from `MKE2FS_CONFIG`, system config, or built-in default profile.
- Sets locale, error tables, PATH, page size, and initial superblock revision.
- Parses CLI options for block/cluster size, bad blocks, source population, direct I/O, extended options, journal options, labels, UUIDs, features, filesystem type, usage type, undo file, force/noaction modes, and recovery-only superblock mode.
- Determines device size, creates a regular file if needed and size was explicit, and checks mount/plausibility unless forced.
- Resolves fs type stack from invocation name, `-t`, `-T`, per-device profile, defaults, and size-derived usage class.

2. Profile and feature resolution
- `parse_fs_type()` builds ordered fs type/usage list, with size classes `floppy`, `small`, `default`, `big`, and `huge`.
- For Hurd targets, it forces or appends Hurd-compatible behavior.
- `get_string_from_profile()`, `get_int_from_profile()`, `get_uint_from_profile()`, `get_double_from_profile()`, and `get_bool_from_profile()` merge `[defaults]` and `[fs_types]` values.
- Base features, cumulative `features`, default mount options, and `default_features` are applied through e2p editing helpers.
- Hurd-incompatible features such as filetype, huge_file, metadata_csum, ea_inode, and casefold are cleared or rejected depending on user intent.

3. Extended option parsing
- `parse_extended_opts()` handles comma-separated `-E` and profile `options` settings.
- Supported options include descriptor size, hash seed, offset, MMP interval, no_copy_xattrs, sparse_super2 backup count, packed metadata, RAID stride/stripe, online resize reservation, revision, test_fs, lazy inode/journal initialization, prezeroed storage assumption, root owner/perms/SELinux label, discard/nodiscard, quota types, Android sparse output, casefold encoding/flags, and orphan file size.
- It validates arguments immediately and exits with a detailed valid-option list on malformed input.
- It enforces encoding flag use only when encoding/casefold is active.

4. Device and layout derivation
- Reads logical and physical sector sizes, with environment overrides.
- Uses blkid topology when available to derive minimum/optimal I/O, alignment offset, DAX capability, and RAID stride/stripe defaults.
- Applies blocksize, cluster size, inode ratio, inode size, flex_bg size, reserved blocks, sparse_super2 backups, 64-bit constraints, and feature dependency checks.
- Rejects incompatible combinations such as 64bit without extents, verity without extents, bigalloc without extents, resize_inode with meta_bg, resize_inode without sparse_super, and project quota with too-small inodes.
- Warns for deprecated 128-byte inode date limits when configured to do so.

5. Filesystem creation in `main()`
- Calls `PRS()`, selects the I/O manager, and optionally wraps it with undo I/O via `mke2fs_setup_tdb()`.
- Initializes the filesystem with `ext2fs_initialize()`, or sparse Android output via `sparse_io_manager`.
- Applies error behavior from profile/CLI.
- Computes journal sizing through `figure_journal_size()` when needed.
- Applies I/O channel options including undo data size and filesystem offset.
- Handles `assume_storage_prezeroed` and discard. Successful discard that guarantees zero reads lets mke2fs skip inode table wiping and hugefile zeroing.
- Zaps old superblock/boot/terminal metadata sectors where appropriate.
- Generates or parses filesystem UUID, initializes checksum seed, directory hash seed, check intervals, creator OS, volume label, last-mounted path, encryption algorithms, and checksum type.
- Shows summary stats and supports `-n` noaction exit.

6. Metadata construction
- Reads or generates bad block lists and marks them used.
- Allocates group tables either normally or with `packed_allocate_tables()` for packed flex_bg metadata.
- Converts bitmaps for subcluster accounting and calculates overhead.
- In normal mode:
  - zeros end-of-device metadata area,
  - writes inode tables,
  - creates root directory,
  - creates `/lost+found`,
  - reserves special inodes,
  - creates bad block inode,
  - creates resize inode if enabled.
- In `-S` super-only mode:
  - warns and marks filesystem erroneous,
  - avoids dirtying bitmaps,
  - preserves inode usage assumptions for later e2fsck recovery.

7. Optional feature materialization
- Creates external journal devices with `create_journal_dev()` or attaches external journals.
- Creates internal journal inode with `ext2fs_add_journal_inode3()`.
- Initializes MMP if enabled.
- Fixes bigalloc group free counts.
- Creates quota inodes when quota feature is enabled.
- Creates orphan file when orphan_file feature is enabled and journaling is present.
- Calls `mk_hugefiles()` for configured preallocated huge files.
- Copies a source directory/tarball/stdin tree into the filesystem via `populate_fs3()` when `-d` is used.
- Closes and writes superblocks/accounting through `ext2fs_close_free()`.

Important helper functions:
- Bad block handling: `read_bb_file()`, `test_disk()`, `handle_bad_blocks()`, `create_bad_block_inode()`.
- Metadata zeroing/layout: `write_inode_tables()`, `packed_allocate_tables()`, `zap_sector()`.
- Directory/bootstrap: `create_root_dir()`, `create_lost_and_found()`, `reserve_inodes()`.
- Journal device support: `create_journal_dev()`.
- Display: `show_stats()`.
- OS handling: `for_hurd()`, `set_os()`.
- Undo/discard: `should_do_undo()`, `mke2fs_setup_tdb()`, `mke2fs_discard_device()`.
- Accounting: `fix_cluster_bg_counts()`, `create_quota_inodes()`, `set_error_behavior()`.

Important dependencies:
- libext2fs for all on-disk ext metadata creation.
- e2p for feature/mount option parsing, UUID/encoding display helpers, and hashing constants.
- support profile library for `mke2fs.conf`.
- blkid for topology probing.
- quota support for internal quota inode creation.
- create_inode support for `-d` population.
- `mk_hugefiles.c` through `mke2fs.h`.

Research notes:
- The formatter is deliberately profile-driven: command line values override profile defaults, but many defaults are derived late after fs type and device size are known.
- Many safety checks happen before `ext2fs_initialize()`, but some dependency checks happen after the initialized filesystem exists because they depend on finalized superblock values.
- The file treats discard as irreversible with respect to undo, so discard is skipped when using undo I/O.
- `mke2fs.c` is the coordination center for config templates and man-page behavior in this group.
