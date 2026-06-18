# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/feature_quota.c

## Purpose
Enables and disables user and group quota features.

## Main Behavior
- `create_system_file()` creates missing quota system inodes and links them in the system directory.
- `create_quota_files()`:
  - Creates the global quota file and per-slot local quota files.
  - Initializes global and local quota files.
  - Computes current quota usage by scanning the filesystem.
  - Writes quota usage to disk.
- `remove_quota_files()` iterates the system directory and deletes matching `aquota.user`, `aquota.group`, and per-slot suffixed files.
- `enable_usrquota()` / `enable_grpquota()` create quota files and set the matching RO-compatible feature bit.
- `disable_usrquota()` / `disable_grpquota()` delete quota files and clear the matching feature bit.
- Defines two features:
  - `usrquota_feature`
  - `grpquota_feature`

## Dependencies
- OCFS2 quota APIs, system inode creation/linking, directory iteration, inode truncation/delete.
- Tunefs progress, signal blocking, and allocator checks.

## Notes
Quota enable is not just a superblock flag: it materializes quota system files and computes initial usage. Disable removes quota files from the system directory.
