# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfstruncate.8.in

## File Role

`ntfstruncate.8.in` is the manual page template for the `ntfstruncate` utility. It describes the tool as truncating or extending a specified NTFS attribute belonging to a file or directory.

The documented synopsis is:

`ntfstruncate [options] device file [attr-type [attr-name]] new-length`

This presents the target as a file path, not an inode number.

## Documented Interface

The page documents these options:

- `-f`, `--force`: override safety checks such as refusing mounted volumes
- `-h`, `--help`: show help
- `-l`: show license
- `-n`, `--no-action`: simulate without writing
- `-q`, `--quiet`: suppress output
- `-v`, `--verbose`: increase output
- `-V`, `--version`: print version/copyright/license

It also documents advanced attribute selection by numeric NTFS attribute type and optional attribute name. The attribute table lists common NTFS attribute IDs from `$STANDARD_INFORMATION` (`0x10`) through `$LOGGED_UTILITY_STREAM` (`0x100`), with `$DATA` (`0x80`) as the default.

`new-length` is described as accepting decimal sizes plus SI suffixes (`K`, `M`, `G`, `T`, `P`, `E`) and binary suffixes (`Ki`, `Mi`, `Gi`, `Ti`, `Pi`, `Ei`), rounded to a cluster-size multiple.

## Examples and Context

The example shows resizing `/Data/database.db` to `100M` on `/dev/sda1`.

The page links `ntfstruncate` with `ntfs-3g`, `ntfsfallocate`, and `ntfsprogs`, and says it is part of the ntfs-3g package.

## Notable Mismatch

The implementation in `ntfstruncate.c` parses the second positional argument as an MFT inode number, and parses `new-length` with plain `strtoll()` without suffix handling. This man page therefore documents a more user-facing pathname/suffixed-size interface than the current C implementation actually provides.
