# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfscat.8.in

## Role

This is the roff manual page template for `ntfscat`, an ntfs-3g utility that prints an NTFS file or stream to standard output.

## Documented Behavior

- Reads from an NTFS volume and writes selected file/stream contents to stdout.
- Filename lookup is documented as case-insensitive.
- A file can be selected by path or by inode number.
- The default output is the unnamed `$DATA` attribute unless another attribute type is requested.

## Options

- `-a, --attribute TYPE`: select an attribute by decimal, hexadecimal, or symbolic name. The manual lists standard NTFS attribute type ids from `$STANDARD_INFORMATION` through `$LOGGED_UTILITY_STREAM`.
- `-n, --attribute-name NAME`: select a named attribute/stream.
- `-i, --inode NUM`: select file by inode instead of pathname.
- `-f, --force`: override safety defaults, such as mounted-volume checks.
- `-h, --help`, `-q, --quiet`, `-V, --version`, `-v, --verbose`: standard utility controls.

## Examples

The examples show reading `/boot.ini`, reading a nested path such as `/winnt/system32/drivers/etc/hosts`, and dumping the root directory `$INDEX_ROOT` by inode 5 through `hexdump`.

## Cross References

The page points users at `libntfs(8)` for encrypted-file access details and references `ntfsls(8)` and `ntfsprogs(8)`.
