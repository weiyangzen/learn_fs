<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/metadata.py -->
# sources/sync-backup/bup/lib/bup/metadata.py

## Purpose
This module captures, serializes, displays, creates, and restores filesystem metadata for bup archives. It handles common stat fields, ownership, timestamps, paths, symlink targets, hardlink targets, POSIX ACLs, Linux file attributes, and Linux xattrs.

## Important APIs, Types, And Functions
Core APIs include `Metadata`, `ApplyError`, `empty_metadata`, `from_path()`, `save_tree()`, `summary_bytes()`, `detailed_bytes()`, `display_archive()`, `start_extract()`, `finish_extract()`, and `extract()`. Internal record handlers encode/load/apply tagged fields such as common records, path, symlink target, hardlink target, POSIX1e ACL, Linux attr, and Linux xattr.

## Control Flow
`from_path()` lstat's a path, optionally calls a race-test hook, collects common fields and optional platform metadata, then freezes the object. `Metadata.encode()` emits a sequence of vint-tagged records ending with tag 0; `Metadata.read()` dispatches tags, supports legacy common/ACL formats, skips unknown bvec records, and returns `empty_metadata` for empty entries. Extraction creates paths first, then applies metadata, deferring directories until longest-path-first order to preserve directory permissions and times.

## State And Persistence Behavior
Persistent metadata lives in `.bupm` streams and `bupindex.meta`. Record tags are private and explicitly stable. Module state includes optional xattr/ACL/Linux attr backends, warning suppression flags, `verbose`, and `empty_metadata`. Restore mutates the filesystem: creates/unlinks paths, changes ownership/mode/times, sets ACLs, attrs, and xattrs when supported.

## Dependencies And Integration Points
It depends on `vint`, `xstat`, recursive directory scanning, `pwdgrp`, `_helpers` ACL/attr functions, optional xattr modules, and helpers for logging/errors. It is consumed by index metadata stores, VFS metadata augmentation, save/restore/get rewrite flows, and `ls` long output.

## Risks And Edge Cases
The file notes that metadata encoding is not stable. Restore is platform-sensitive: symlink chmod support, ACL/xattr availability, superuser ownership semantics, socket creation fallback, Linux attr API suppression on some big-endian ABIs, and unsupported filesystems all affect results. Path cleanup is security critical and rejects risky extraction paths. `finish_extract()` checks `os.path.isdir(meta.path)` rather than the cleaned path in one branch, which deserves scrutiny. Non-empty directories are not overwritten during creation.

## Test Signals
`test/int/test_metadata.py`, `test/ext/test-meta`, `test/ext/test-meta-acls`, `test/ext/test-empty-metadata`, `test/ext/test-save-restore`, `test/ext/test-restore-map-owner`, `test/ext/test-restore-single-file`, and VFS tests cover serialization, path cleanup, xattrs/ACLs, owner mapping, symlink races, empty metadata, and extraction ordering.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/metadata.py -->
