# File Research: sources/os/plan9/9front/sys/src/9/xen/xenelf.c

Purpose: User-space ELF rewriter for Xen boot images. It page-aligns program segments and appends a named section containing supplied string contents.

Key behavior:
- Reads ELF header/program headers with explicit little-endian helpers.
- Copies loadable segments to page-aligned offsets and rounds `filesz`/`memsz` for `LOAD` segments.
- Copies extra symbol/line data for non-load segments using `memsz`.
- Appends a minimal section-name string table and one new section named by the caller.
- Rewrites ELF section-header metadata.

Integration notes: Invoked as `xenelf input output section-name section-contents`. Includes `/sys/src/libmach/elf.h`.

Risk/attention points: Existing section headers are effectively ignored (`ns = 0`), so the output is intentionally minimal. Error checking on I/O is sparse.
