# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfsclone.8.in

## Role

This is the roff manual page template for `ntfsclone`, the ntfs-3g sector-level NTFS cloning, imaging, restore, rescue, and metadata-copy utility.

## Documented Behavior

- `ntfsclone` copies only used NTFS data at disk-sector level.
- Unused space is represented differently depending on target mode:
  - sparse holes when cloning to sparse files;
  - control codes in the special image format;
  - unchanged space when cloning to an existing partition/device;
  - zero-filled output when writing to stdout.
- Non-image clones are exact sector-level NTFS filesystem copies and can be mounted like the original.
- The utility is explicitly filesystem-focused and does not solve Windows boot migration issues such as partition start sector and BIOS geometry dependencies.

## Major Modes

- Normal clone to file/stdout/device.
- `--save-image`: write the special ntfsclone image format.
- `--restore-image`: restore from that image format, including stdin via `-`.
- `--metadata`: copy only NTFS metadata while wiping file contents and most resident user data.
- Rescue mode: ignore disk read errors and mark unreadable sectors with a recognizable marker and filler.

## Options

- `-o, --output FILE`: clone to a non-existent file or stdout.
- `-O, --overwrite FILE`: clone to an existing partition/device or file.
- `-s, --save-image`, `-r, --restore-image`, `-n, --no-action`.
- `--rescue`: continue past read errors.
- `-m, --metadata`: metadata-only clone, limited to sparse file unless combined with save-image.
- `--ignore-fs-check`: metadata-only safety override for consistency-check failures.
- `-t, --preserve-timestamps`: preserve timestamps in metadata-only mode.
- `--full-logfile`: include Windows log file, useful for dirty filesystems and metadata extraction.
- `--new-serial`, `--new-half-serial`: randomize full or upper half of NTFS serial for coexistence with the source filesystem.
- `-f, --force`, `-q, --quiet`, `-h, --help`.

## Operational Guidance

The manual explains sparse-file behavior, limitations of common Linux tools with large sparse files, the purpose of the special image format for streaming/compression, and the privacy limits of metadata-only images. It states metadata-only mode wipes file contents, timestamps unless preserved, and unused metadata spaces, but filenames remain visible and may be sensitive.

## Examples

Examples cover cloning between devices, saving/restoring image files, gzip pipelines, remote ssh backup/restore streams, web-stream restore, sparse-file clone creation, and metadata-only image compression/unpacking.

## Cross References

The page references `ntfsresize(8)`, `ntfsprogs(8)`, `xfs_copy(8)`, `debugreiserfs(8)`, and `e2image(8)`.
