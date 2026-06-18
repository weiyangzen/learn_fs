# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfsinfo.8.in

## Role

`ntfsinfo.8.in` is the manual page template for `ntfsinfo`, describing it as a utility to dump attributes for an inode or path and/or volume/MFT information.

## Documented Interface

The manpage documents:

- `-F/--file FILE`: inspect a file by absolute path.
- `-i/--inode NUM`: inspect an inode/MFT record.
- `-m/--mft`: show volume information.
- `-t/--notime`: suppress timestamps.
- `-f/--force`: use less caution.
- `-q/--quiet`, `-v/--verbose`.
- `-h/--help`, `-V/--version`.

## Relationship To Implementation

The documented read-only inspection role matches `ntfsinfo.c`. One mismatch is important: the C option table maps long `--notime` to `T`, but the parser treats `T` as deprecated/error and accepts lowercase `-t` as the working notime option. The manpage says `--notime` works.

## Notes

The BUGS section says there are no known problems, but `ntfsinfo.c` contains a substantial TODO list and several incomplete attribute dumpers.
