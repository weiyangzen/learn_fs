# File Research: sources/os/bsd/freebsd-src/sbin/ldconfig/elfhints.c

## Purpose
Implements ELF hints file reading, listing, directory validation, and atomic writing for `ldconfig`.

## Main Responsibilities
- Maintains a bounded directory list for runtime linker search hints.
- Reads existing ELF hints files.
- Reads directories from command-line arguments or list files.
- Applies security checks to untrusted directories.
- Writes updated hints files with selected endianness.
- Lists search directories and discovered shared libraries.

## Key Implementation Details
- `add_dir()` rejects untrusted directories that are not root-owned or are group/world-writable unless `insecure` is set.
- `list_elf_hints()` prints search directories and scans them for `lib*.so.<version>` names.
- `read_dirs_from_file()` parses whitespace-separated directory list files, ignoring comments and warning on trailing characters.
- `read_elf_hints()` mmaps an existing hints file privately, validates magic/version, handles forced big-endian compatibility, and extracts the colon-separated directory list.
- `COND_SWAP()` abstracts little-endian versus big-endian hints format conversion.
- `update_elf_hints()` optionally merges existing hints, treats regular files as directory-list files, and writes the final hints file.
- `write_elf_hints()` writes to `hintsfile.XXXXXX`, chmods it `0444`, writes the header and string table, then renames atomically.

## Data Constraints
- Maximum directories: `1024`.
- Maximum hints file size: `16 KiB`.

## Notable Edge Cases
- Missing hints files are allowed only when `must_exist` is false.
- Hints files with unexpected endianness are rejected when `force_be` is requested.
- Directory strings from an mmap are temporarily split in place because mapping is private writable.
