# sources/sync-backup/kopia/internal/gather/gather_bytes.go

Purpose: represents binary data as a logical byte sequence backed by multiple slices, avoiding mandatory contiguous allocation for large buffers.

Important APIs/types/functions: `Bytes`, `ErrInvalidOffset`, `FromSlice`, `Length`, `AppendSectionTo`, `ReadAt`, `Reader`, `AppendToSlice`, `ToByteSlice`, `WriteTo`, and internal `bytesReadSeekCloser`. The invalidation sentinel uses a generated UUID byte slice.

Control flow: `AppendSectionTo` walks slices to locate the starting offset, writes the first partial slice, then writes whole or partial subsequent slices until `size` is satisfied. `bytesReadSeekCloser.ReadAt` performs similar offset lookup and copies into caller-provided memory, returning `ErrInvalidOffset` for negative offsets and `io.EOF` when data is exhausted. `Reader` returns a seekable read closer over a value copy of `Bytes`.

State/persistence behavior: `Bytes` is a view over existing slices; it does not own or copy them except in `ToByteSlice`. `WriteBuffer.Close` can invalidate exposed `Bytes`, after which methods panic via `assertValid`.

Dependencies/integration: used across content buffering, HMAC, blob storage, and gather write buffers. Implements common I/O interfaces expected by storage code.

Risks/test signals: `Bytes.ReadAt` currently returns `len(p)` with the error from `AppendSectionTo`, so the more precise `ReaderAt` behavior lives in `bytesReadSeekCloser`. Consumers must not use `Bytes` after the owning buffer closes.
