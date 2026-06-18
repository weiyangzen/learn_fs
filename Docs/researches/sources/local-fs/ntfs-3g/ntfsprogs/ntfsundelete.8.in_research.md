# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfsundelete.8.in

## File Role

`ntfsundelete.8.in` is the manual page template for `ntfsundelete`, documenting recovery of deleted files from an NTFS volume.

It describes three modes:

- scan: default, list deleted files and recovery likelihood
- undelete: recover files selected by inode range or name pattern
- copy: expert/debug mode that copies MFT record ranges to a host file

The page emphasizes that `ntfsundelete` only reads the NTFS volume and never modifies it.

## Documented Behavior

The caveats section explains important recovery limits:

- deleted data may already have been overwritten
- MFT records may be reused
- extended/multi-record metadata is not reconstructed
- compressed and encrypted files cannot be recovered
- recovered file size and dates may be unreliable because deleted metadata can be inconsistent

The scan output is documented as:

`Inode Flags %age Date Time Size Filename`

with flags for file/directory, resident/nonresident stream, compressed/encrypted stream, and missing/multi-record attributes.

## Documented Options

Main scan filters:

- `-m`, `--match PATTERN`
- `-C`, `--case`
- `-p`, `--percentage NUM`
- `-S`, `--size RANGE`
- `-t`, `--time SINCE`
- `-P`, `--parent` with verbose output

Recovery options:

- `-u`, `--undelete`
- `-i`, `--inodes RANGE`
- `-o`, `--output FILE`
- `-d`, `--destination DIR`
- `-b`, `--byte NUM`
- `-O`, `--optimistic`
- `-T`, `--truncate`

Copy/debug option:

- `-c`, `--copy RANGE`

General options:

- `-f`, `--force`
- `-q`, `--quiet`
- `-v`, `--verbose`
- `-V`, `--version`
- `-h`, `--help`

## Examples

The examples cover scanning a device, matching `*.doc`, filtering by size/percentage/time, undeleting explicit inode ranges, recovering with a custom output path and exact truncation, and copying MFT records to a debug file.

## Integration Notes

The documented behavior aligns closely with `ntfsundelete.c`: read-only volume access, host-side recovered output files, wildcard matching, inode ranges, and MFT-copy mode are all implemented.
