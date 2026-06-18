# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/portfns.h

This header declares most KFS internal functions and vararg format checks.

Key areas:
- Metadata/block helpers: `accessdir`, `balloc`, `bfree`, `checktag`, `dnodebuf`, `dtrunc`, `getbuf`, `putbuf`, `settag`.
- Fid/path helpers: `fileinit`, `filep`, `newfp`, `freefp`, `newwp`, `freewp`, `putwp`.
- Protocol helpers: `mkqid`, `mkqidcmp`, `mkqid9p1`, `mkqid9p2`, `serve9p1`, `serve9p2`.
- Console helpers: `con_*`, `cmd_user`, `cprint`.
- Auth/user helpers: `authfree`, `mkchallenge`, `ingroup`, `leadgroup`, `strtouid`, `uidtostr`.
- Formatting helpers and `#pragma varargck` declarations for custom formats.

Role:
- Shared prototype surface for the old C codebase, compensating for pre-ANSI style definitions and cross-file dependencies.
