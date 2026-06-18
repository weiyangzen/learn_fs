# File Research: sources/os/bsd/freebsd-src/sbin/mdconfig/mdconfig.c

## Summary
Implements the `mdconfig` command-line utility for creating, destroying, resizing, querying, and listing FreeBSD memory disks backed by malloc memory, vnode files, swap, or null storage.

## Main Responsibilities
- Parses `-a`, `-d`, `-r`, and `-l` actions and validates incompatible option combinations.
- Builds `struct md_ioctl` requests for `MDIOCATTACH`, `MDIOCDETACH`, `MDIOCRESIZE`, and `MDIOCQUERY`.
- Infers vnode or swap type when `-t` is omitted.
- Parses human-readable sizes with block, byte, KB, MB, GB, TB, and PB suffixes.
- Validates vnode backing files with `realpath`, `open`, `fstat`, and regular-file checks.
- Loads `geom_md` when needed and opens `/dev/mdctl`.
- Lists devices using GEOM tree/stat snapshots, with optional verbose output and file filtering.

## Key Functions
- `main()`: option parsing, action validation, ioctl dispatch.
- `md_set_file()`: canonicalizes and validates vnode backing file and default size.
- `md_list()` / `md_query()`: traverse GEOM providers in class `MD`.
- `print_options()`: queries a unit and prints enabled md options.
- `md_find()`: matches comma-separated md unit/device names.
- `md_prthumanval()`: humanizes provider byte lengths.

## Dependencies And Integration
Includes `<sys/mdioctl.h>`, `<libgeom.h>`, `<libutil.h>`, and devstat/GEOM APIs. It is the userland control path for the `geom_md` kernel module and md(4) providers.

## Research Notes
The code has careful command-line compatibility behavior: `mdconfig file` implies attach-vnode mode, `-n` suppresses the `md` prefix in some output, and read-only vnode mode is auto-enabled when the backing file cannot be opened writable.
