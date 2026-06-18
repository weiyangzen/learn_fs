# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/malloc_.h

## Purpose
Ghostscript portability wrapper for `malloc.h`/allocation declarations across old C libraries and platforms.

## Main Structure
- Includes `std.h` first to satisfy Ghostscript ordering requirements.
- Selects `<alloc.h>`, `<stdlib.h>`, `<malloc.h>`, or manual `malloc`/`free` declarations depending on compiler/platform macros.
- Defines `gs_realloc` as either a Ghostscript replacement or a direct `realloc` wrapper.

## Integration Notes
- Used by `lib.mak` dependency graph as `malloc__h`.
- On Linux defines `malloc__need_realloc` and declares `gs_realloc(void *, size_t, size_t)`.

## Risks and Edge Cases
- Contains historical platform conditionals for very old compilers/Unix variants.
- Linux realloc substitution changes call semantics to include old and new sizes.
