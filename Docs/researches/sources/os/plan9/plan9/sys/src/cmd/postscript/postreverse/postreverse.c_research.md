# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/postreverse/postreverse.c

PostScript page-order reverser for structurally commented PostScript files.

Key responsibilities:
- Reorders pages using Adobe structuring comments and package-specific comments.
- Copies the prologue/setup/trailer while reversing selected page bodies.
- Moves page-local global definitions bracketed by `%%BeginGlobal`/`%%EndGlobal` into the prologue/setup section.
- Supports documents using `%%Page:` starts, `%%EndPage:` ends, or both.
- Handles multiple forms per physical page by reversing sheets while preserving subpage order and adding dummy pages as needed.
- Supports page selection, no-reverse mode, version override for dummy-page behavior, temporary directory override, debug, and ignore-fatal options.

Control flow:
- `arguments()` accepts at most one input file, or copies stdin to a temporary file.
- `reverse()` copies through `%%EndProlog`, records pages/globals, writes pages in new order, and copies trailer content.
- `moreprolog(str)` copies input until a target comment, updating `forms` and `version` from structuring comments.
- `readpages()` records page start/stop offsets in `pages[]`, detects setup sections, extracts global sections, and finds trailer offset.
- `writepages()` emits the end of prologue/setup, pads dummy pages when reversing multi-form documents, then copies real pages in reverse sheet order.
- `copypage()` copies a page range while skipping `%%BeginGlobal`/`%%EndGlobal` sections.
- `trailer()` copies everything after `%%Trailer`.

Important behavior:
- `-r` disables reversal but still normalizes global definitions, by setting `forms = next_page` in `writepages()`.
- Empty dummy pages are emitted differently depending on input `version` and `ignoreversion`.
- If no `%%EndProlog` is found, the file is copied through unchanged.
- If stdin is used, the input is read into a temp file and then processed with random-access `ftell()`/`fseek()`.

Dependencies:
- Shared common layer: `comments.h`, `gen.h`, `path.h`, `ext.h`, `out_list()`, `error()`, `interrupt()`, and `temp_file`.
- Local `Pages` struct from `postreverse.h`.

Risks and quirks:
- Fixed `pages[1000]` page table can overflow on larger jobs.
- Uses `ftell()`/`fseek()` and text-mode line lengths; very long lines beyond `buf[2048]` can break comment detection.
- `copystdin()` uses tempnam-style temp-file creation.
- Everything between consecutive `%%EndPage:` and `%%Page:` comments is intentionally ignored, per comments.
