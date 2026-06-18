# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfsls.8.in

## Role

`ntfsls.8.in` is the manual page template for `ntfsls`, documenting directory and file listing inside an NTFS filesystem or image.

## Documented Interface

The manpage documents:

- `-p/--path PATH`: directory or file to list.
- `-a/--all`: include all files / POSIX namespace entries.
- `-s/--system`: include system files.
- `-x/--dos`: show DOS 8.3 names instead of Win32 names.
- `-l/--long`: long listing.
- `-i/--inode`: include MFT reference.
- `-F/--classify`: append classification indicator.
- `-R/--recursive`: recurse below the requested directory.
- `-f`, `-q`, `-v`, `-V`, `-h`.

## Relationship To Implementation

The option list matches `ntfsls.c`. The expanded synopsis omits `-R/--recursive`, although the option is documented in the OPTIONS section and implemented.

## Notes

The documentation says the default path is the root directory and the device may be a block device or NTFS image file. This matches the implementation’s default `opts.path = "/"` and `utils_mount_volume()` usage.
