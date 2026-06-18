# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/data.c

Static diagnostic string tables for cwfs.

Important contents:
- `errstr9p` maps internal cwfs error codes to 9P error strings.
- `wormscode` maps optical/WORM device sense/error codes to human-readable diagnostics.
- `tagnames` maps block tag enum values to names such as `Tdir`, `Tfile`, `Tfree`, indirect tags, `Tsuper`, `Tvirgo`, and `Tcache`.
- These strings are consumed by 9P error replies, check/debug output, and cache-worm diagnostics.
