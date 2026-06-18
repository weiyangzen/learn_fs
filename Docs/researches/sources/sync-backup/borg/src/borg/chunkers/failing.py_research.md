# sources/sync-backup/borg/src/borg/chunkers/failing.py

Purpose: provides `ChunkerFailing`, a deterministic test chunker that can simulate read successes and I/O errors by block position.

Important APIs: `ChunkerFailing(block_size, map)` validates a map of `R`/`E` behavior characters, tracks block count, and exposes `chunking_time` for caller compatibility. `chunkify(fd=None, fh=-1)` reads from an OS file handle or Python file object, emits `Chunk(data, size=got, allocation=CH_DATA)` for `R`, raises `OSError(errno.EIO, "simulated I/O error", fname)` for `E`, and repeats the last map behavior beyond map length.

Control flow and state: state is per chunker instance through `self.count`. It stops when a read returns fewer bytes than `block_size`, treating that as EOF after yielding any final successful partial chunk.

Dependencies and integration: imports `Chunk` from `.reader` and `CH_DATA` from constants. Used by `get_chunker("fail", ...)`, mainly for tests of error handling in archive creation/chunk processing paths.

Risks: because the final map character repeats indefinitely, short maps can simulate persistent failures or successes. It does not update timing, hash, or sparse metadata beyond `CH_DATA`, so it should not be used as production logic.

Test signals: validate map parsing, file object and file descriptor paths, partial final reads, repeated final behavior, emitted chunk metadata, and exception filename inclusion for file-object reads.
