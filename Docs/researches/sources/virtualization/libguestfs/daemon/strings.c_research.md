# File Research: sources/virtualization/libguestfs/daemon/strings.c

Wraps GNU `strings`.

Important behavior:
- `do_strings_e` validates encoding is one of `sSblBL`.
- Opens the guest file under chroot and copies fd to command stdin.
- Runs `strings -a -e <encoding>`.
- Splits stdout into returned lines.
- `do_strings` defaults to encoding `"s"`.

Filesystem relevance: extracts printable strings from guest files for inspection.
