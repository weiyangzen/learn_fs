# sources/user-network-fs/nfs-utils/support/nfs/xio.c

Purpose: tokenized file I/O helpers for exports-style configuration files.

Important APIs: `xfopen()`, `xfclose()`, `xflock()`, `xfunlock()`, `xgettok()`, `xgetc()`, `xungetc()`, `xskip()`, and `xskipcomment()`. `XFILE` wraps a `FILE *` and current line number.

Control flow: `xgetc()` handles backslash-newline continuations by returning a space and incrementing the line number. `xgettok()` reads until whitespace or a requested separator unless inside double quotes, decodes octal `\nnn` escapes, and returns 0 for no token, 1 for success, or -1 for overflow/separator mismatch. `xskip()` skips caller-specified chars and comments beginning with `#`.

State and persistence: file position and line number live in `XFILE`. `xflock()` creates/opens lock files and returns an fd whose close releases the fcntl lock.

Dependencies and integration: used by `exports.c` and related parsers. Depends on `xmalloc`, `xlog`, and standard stdio/fcntl APIs.

Risks: token length overflow returns -1 after consuming input. Quote handling toggles on every `"`, with no escape-specific quote semantics. `xflock()` opens read locks with `O_CREAT`, which can create missing lock files even for read mode.

Test signals: quoted tokens, separators, octal decoding, line continuation, comments, line-number pushback, token overflow, and fcntl lock acquisition/release.
