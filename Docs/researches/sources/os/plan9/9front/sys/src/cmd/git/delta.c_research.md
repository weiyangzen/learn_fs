# File Research: sources/os/plan9/9front/sys/src/cmd/git/delta.c

Content-defined delta generator for git pack writing.

Key responsibilities:
- Splits a base object into rolling gear-hash chunks.
- Builds an open-addressed hash table from base chunks.
- Splits the target object the same way, looks up matching chunks, and emits copy or insert delta spans.
- Extends copy spans forward while bytes continue matching.
- Manages delta table object references and memory.

Important behavior:
- Chunk sizes range from 128 to 8192 bytes with split mask `(1<<8)-1`.
- Uses `murmurhash2()` for table lookup keys.
- Copy lengths are capped below Git’s 24-bit delta length limit.

Notable risks:
- The algorithm emits one delta op per chunk/span and does not coalesce adjacent compatible ops.
