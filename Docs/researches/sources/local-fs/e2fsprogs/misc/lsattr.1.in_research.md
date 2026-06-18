# File Research: sources/local-fs/e2fsprogs/misc/lsattr.1.in

## Purpose
Manpage source for `lsattr`, which lists ext2/ext3/ext4 file attributes.

## Key Elements
Documents recursive listing, version display, all-files listing, directory-as-file handling, long option names, project number display, and generation/version display.

## Dependencies
References `chattr(1)` for attribute meanings and e2fsprogs availability.

## Behavior/Risks
Documentation-only. It intentionally delegates semantic explanation of individual attribute flags to `chattr`.
