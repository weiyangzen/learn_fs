# sources/sync-backup/casync/test/test-cachunk.c

Purpose: unit-style test for chunk file read/write helpers.

Important APIs/types/functions: `test_chunk_file` generates random bytes, writes them to a temp fd, reads via `ca_chunk_file`, validates `ReallocBuffer` contents, rewrites via `ca_chunk_write`, tests digest/id behavior, and compares bytes.

Control flow/state: uses a temporary unlinked file and two `ReallocBuffer` instances. State is fully local and cleaned by fd close/buffer free.

Dependencies/integration: exercises chunking, digest, realloc-buffer, random, and tmp-dir utilities.

Risks/test signals: random content increases coverage but can make failures harder to reproduce without captured data. It validates full-buffer equality rather than only return codes.

Source research group: `subset-b-009122`.
