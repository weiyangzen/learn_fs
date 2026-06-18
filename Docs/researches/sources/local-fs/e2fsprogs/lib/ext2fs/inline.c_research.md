# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/inline.c

## Role

Exports formerly inline header helpers as linkable functions, chiefly aligned memory allocation.

## Main Flow

- `ext2fs_get_memalign()` normalizes alignment to at least 8.
- Prefers `posix_memalign`, falls back to `memalign`, then `valloc` or `malloc` with manual alignment check depending on platform support.
- Maps `ENOMEM` to `EXT2_ET_NO_MEMORY` where appropriate.

## Dependencies

Includes `ext2fs.h` with `INCLUDE_INLINE_FUNCS` so header inline definitions are emitted here.

## Risks / Notes

- The fallback `malloc` path cannot adjust returned pointers; if the pointer is not aligned, it frees and fails.
- Debug-only self-test checks several alignments.
