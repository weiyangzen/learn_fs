# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/tr2post/tr2post.c

Purpose: Main program for converting troff device-independent output to PostScript.

Key behavior:
- Parses options for aspect ratio, copies, debug, magnification, forms per page, page list, orientation, offsets, and PostScript passthrough.
- Writes converted page body to a temporary file first.
- Reads device `DESC`, converts stdin or input files via `conv`, then closes temp output.
- Reopens stdout, emits final prologue/setup, copies temporary body to stdout, and writes trailer.
- `prologues` conditionally includes base dpost prologue, drawing prologue if any drawing was used, round page support, encoding, forms setup, passthrough, and charlib definitions for built characters.
- `cleanup` removes the temp file at exit.

Dependencies and integration:
- Coordinates all `tr2post` modules.
- Uses `comments.h`, `path.h`, `common.h`, font/DESC loaders, page-list support, and global `Bstdout`.

Risks and notes:
- Uses `tmpnam`, which is unsafe by modern standards.
- Delayed prologue emission is necessary because draw/charlib use is discovered during conversion.
- Missing input files are reported and skipped.
