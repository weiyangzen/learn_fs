# sources/object-store/rustfs/crates/io-core/src/reader.rs

Purpose: `Bytes`-backed async reader for object data, with constructors for in-memory data and file ranges.

Important APIs/types: `ZeroCopyReadError` covers I/O, mmap, and invalid range errors. `ZeroCopyObjectReader` stores a `Bytes` and current position. Constructors are `from_bytes`, Unix `from_file_mmap_path`, Unix/non-Unix `from_file_mmap`, plus accessors `remaining_bytes`, `len`, `is_empty`, and `position`. It implements Tokio `AsyncRead`.

Control flow: `from_bytes` wraps an existing `Bytes` without copying. Unix `from_file_mmap_path` opens a file in `spawn_blocking`, creates a `memmap2` mapping for the requested range, then copies the mapped slice into owned `Bytes`. `from_file_mmap` clones/seeks/reads the Tokio file into a `Vec` and converts it to `Bytes`; the non-Unix fallback does the same. `poll_read` copies from the current `Bytes` slice into `ReadBuf`, advances `pos`, and returns ready.

State and persistence: per-reader immutable bytes plus mutable cursor position. No persistence.

Dependencies and integration: uses `bytes`, Tokio async read/seek/file APIs, and `memmap2` for the path-based Unix constructor. Re-exported from `lib.rs`.

Risks: the file constructors are not truly zero-copy because they copy mapped/read data into `Bytes`; docs partially acknowledge the path-based copy but still advertise mmap zero-copy. `InvalidRange` is defined but not used. Reading exact `size` bytes fails if the file is shorter. `poll_read` assumes `self.pos <= self.data.len()`, which holds internally unless future APIs mutate state.

Test signals: tests cover reading from bytes, remaining bytes, position after read, and empty/non-empty state. File-backed constructors are not covered here.
