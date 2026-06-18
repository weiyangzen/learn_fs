# File Research: sources/virtualization/libguestfs/lib/file.c

Purpose: Provides client-side implementations and compatibility wrappers for file read/write/list/stat operations that need local temp files, list chunking, sorting, or old ABI translation.

Key behavior:
- `guestfs_impl_read_file` downloads a guest file to a temp file, reads it fully into memory, NUL-terminates it, and reports size only after success.
- `guestfs_impl_read_lines` splits a downloaded file into LF/CRLF-trimmed string lists.
- `guestfs_impl_find` and `guestfs_impl_ls` use daemon `find0`/`ls0` output, parse NUL-delimited entries, duplicate them, and sort results.
- `write_or_append` uses efficient internal write calls for content up to 2 MiB; larger writes go through temp-file upload. Append uses filesize plus upload offset and is explicitly not atomic.
- `lstatnslist`, `lxattrlist`, and `readlinklist` split large name vectors into batches of 1000 to avoid protocol limits.
- `stat`, `lstat`, and `lstatlist` translate nanosecond stat structures into older `guestfs_stat` ABI structures.

Dependencies and state:
- Depends on generated actions (`download`, `upload`, `find0`, `ls0`, `internal_*`), temp-path helpers, `full_read/full_write`, cleanup macros, and struct cleanup helpers.
- No persistent handle state beyond temp files and errors.

Risks:
- Whole-file reads allocate based on remote/local file size and can be expensive for large files.
- Large append is non-atomic and can race with other writers.
- Empty NUL-delimited outputs require careful parsing; this code has explicit handling but relies on daemon output conventions.
