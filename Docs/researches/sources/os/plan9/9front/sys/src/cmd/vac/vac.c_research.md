# File Research: sources/os/plan9/9front/sys/src/cmd/vac/vac.c

Purpose: Main Vac archive creation command.

Key behavior:
- Parses options for archive mode (`-a`), block size, diff source (`-d`), exclude patterns/files, output file, stdin file name, merge mode, quick diff, temp-file skipping, stats, Venti host, and verbosity.
- Creates a new `VacFs` or opens an archive file read/write and creates dated `yyyy/mmdd[.n]` archive directories.
- Walks input paths, expanding root-like path arguments into directory contents.
- Converts Plan 9 `Dir` metadata into `VacDir`, including permissions, append/exclusive bits, qid path/version, owner/group/muid, times, and size.
- Archives directories recursively and files block-by-block.
- Uses previous archive/diff source entries by copying Venti entries first, then rewriting only blocks whose SHA1 does not match current input.
- Quick diff can skip reading unchanged files based on mtime, size, and Plan 9 qid version metadata.
- Merges `.vac` files by copying root children and shifting qid spaces to avoid overlap.
- Records maximum qid in root qid-space metadata before syncing.

Dependencies:
- Uses Vac filesystem APIs from `file.c`, pattern filtering from `glob.c`, Venti connection APIs, Plan 9 directory APIs, and `sha1matches`.

Notable details:
- `-a` is mutually exclusive with explicit output and diff files because archive mode maintains the file as a rotating archive root.
- `vacmerge` uses qid-space metadata when available and falls back to scanned maximum qid.
