# File Research: sources/local-fs/e2fsprogs/misc/tune2fs.c

## Purpose
Implements `tune2fs`, plus optional `e2label` and `findfs` entry behavior, for inspecting and changing ext2/ext3/ext4 superblock parameters, feature flags, journals, quotas, UUIDs, labels, inode size, MMP state, checksums, and related filesystem metadata.

## Key Elements
Global option state records every command-line mutation request, including mount-count policy, error behavior, reserved block ownership/counts, label and last-mounted strings, UUID changes, feature edits, default mount options, journal settings, quota changes, extended options, inode-size expansion, 64-bit conversion requests, checksum rewrites, undo files, and orphan-file creation.

Feature handling is centered in `update_feature_set`. It validates requested `-O` feature edits against explicit set/clear masks, performs side effects for journal removal/addition, orphan files, sparse superblocks, MMP, dir_index, flex_bg, huge_file, metadata_csum, uninit_bg/GDT checksums, 64bit handoff to `resize2fs`, quota/project flags, encryption defaults, casefold encoding, and metadata_csum_seed. Dangerous operations require clean fsck state, unmounted or read-only constraints, or force flags.

Journal support includes external journal superblock lookup, user UUID table edits, internal journal inode removal, external journal removal, new internal/external journal creation, fast-commit sizing, and journal-user UUID updates when the filesystem UUID changes.

Checksum conversion support rewrites metadata after UUID or feature changes. The directory path adjusts htree limits and directory checksum tails. The inode path rewrites EA inodes first, then directories and other inodes, updating inline xattr hashes, xattr block hashes, extent checksums, directory checksums, inode checksums, group descriptor checksums, MMP checksums, and superblock checksum type/seed fields.

Inode-size expansion is a full metadata migration path: it reads bitmaps, identifies blocks that conflict with expanded inode tables, moves those blocks, fixes inode block references and group descriptor bitmap pointers, rewrites expanded inode tables, updates summary stats, and marks the filesystem invalid until the migration succeeds.

`main`/`tune2fs_main` orchestrates parsing, device resolution, optional ioctl label get/set on mounted Linux filesystems, libext2fs open with MMP handling, optional undo I/O setup, journal recovery, mount checks, requested superblock edits, feature/extended option application, quota updates, UUID replacement through mounted ioctl or direct superblock edit, inode resize, metadata checksum rewrite, superblock listing, and final close/writeout.

## Dependencies
Uses libext2fs extensively for filesystem open/close, bitmaps, inode scanning, block iteration, journal helpers, MMP, orphan files, checksums, group descriptors, directory blocks, xattrs, extents, and superblock fields. It also depends on e2p feature/mount-option parsing and listing, libuuid, blkid device lookup, quota support, com_err, plausible-device checks, devname resolution, undo I/O, and Linux ioctls for live label/UUID operations when available. Shared helper functions and globals are declared in `util.h`.

## Behavior/Risks
This file directly mutates on-disk metadata and has many operation-specific safety gates. Some changes intentionally leave the filesystem needing `e2fsck`, `e2fsck -D`, or `resize2fs`. Checksum and UUID changes can require whole-filesystem inode/directory/xattr rewrites, which are refused on mounted filesystems unless csum-seed semantics make them safe. Inode-size expansion relocates blocks and relies on undo I/O for recoverability; failures direct users to `e2undo`. Force flags can bypass selected safety checks, especially journal/MMP cases, so callers must preserve the command-line semantics carefully.
