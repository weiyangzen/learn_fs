# sources/sync-backup/casync/src/realloc-buffer.c

Purpose: implements a growable byte buffer with efficient front consumption, append, fd read/write, formatted append, and ownership transfer.

Important APIs/types/functions: `realloc_buffer_acquire/acquire0`, `extend/extend0`, `append`, `advance`, `shorten`, `truncate`, `read_size`, `read_full`, `read_target`, `steal`, `donate`, `write`, `write_maybe`, `printf`, and `memchr`. It enforces `REALLOC_BUFFER_MAX` at 1 GiB.

Control flow/state: state is `data`, `allocated`, `start`, and `end`. Growth doubles allocation, aligns to page size, and compacts by copying live data when `start` is nonzero. Read functions append then shrink unused bytes; write drains from the front via `advance`.

Dependencies/integration: uses `page_size`, `mfree`, `memdup`, `BUFFER_SIZE`, and errno conventions from util/def. It is a core buffer primitive for chunk, compression, and protocol code.

Risks/test signals: `realloc_buffer_write` can busy-loop if `write` returns 0, though regular fds should not. Offset arithmetic is guarded, but callers must respect pointer invalidation after growth. `test-cachunk.c` exercises read/write paths indirectly.

Source research group: `subset-b-009122`.
