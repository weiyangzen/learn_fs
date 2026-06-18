# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfsfix.8.in

## Role

Manual page for `ntfsfix`, a utility that fixes limited common NTFS problems and schedules Windows `chkdsk`.

## Documented Interface

Documents `--clear-bad-sectors`, `--clear-dirty`, `--no-action`, `--help`, and `--version`.

## Important Behavior

Clearly states that `ntfsfix` is not a Linux replacement for Windows `chkdsk`; it repairs only fundamental inconsistencies, resets the NTFS journal, and requests a Windows consistency check on next boot.

## Research Notes

This file is documentation only; the implementation is not in this requested group.
