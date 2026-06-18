# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfslabel.8.in

## Role

`ntfslabel.8.in` is the manual page template for `ntfslabel`, documenting display and modification of an NTFS volume label and volume serial number.

## Documented Interface

The manpage documents:

- Default behavior: print current label.
- Positional `new-label`: set the volume label.
- `--new-serial[=ssssssssssssssss]`: set a full 64-bit serial.
- `--new-half-serial[=ssssssss]`: set only the upper serial half.
- `-n/--no-action`: dry run.
- `-f/--force`: operate despite mounted-volume caution.
- `-q`, `-v`, `-V`, `-h`.

## Relationship To Implementation

The serial-number semantics match `ntfslabel.c`: full serial replacement or upper-half replacement, random when no argument is supplied. The manpage’s 128 Unicode character label limit also matches implementation truncation at `0x100` bytes of UTF-16.

## Notes

The document correctly warns that duplicate serial numbers can prevent simultaneous mounts on the same machine and that this serial is not the Windows object-location volume UUID.
