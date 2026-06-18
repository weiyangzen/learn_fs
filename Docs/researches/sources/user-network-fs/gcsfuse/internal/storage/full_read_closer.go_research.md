# sources/user-network-fs/gcsfuse/internal/storage/full_read_closer.go

## Purpose
This file defines `gcsFullReadCloser`, a `gcs.StorageReader` wrapper that normalizes short reads by filling the caller's buffer before returning, unless EOF is reached.

## Important APIs and Control Flow
`newGCSFullReadCloser` wraps an existing `gcs.StorageReader`. `Read` calls `io.ReadFull` on the wrapped reader. If the wrapped reader reaches EOF after returning some bytes, `io.ReadFull` reports `io.ErrUnexpectedEOF`; this wrapper converts that to `io.EOF` so callers see the same terminal error shape as ordinary readers. `ReadHandle` and `Close` delegate directly to the wrapped reader.

## State, Dependencies, and Integration
The only state is the wrapped `gcs.StorageReader`. The wrapper depends on `io`, `cloud.google.com/go/storage` for `ReadHandle`, and the local `gcs.StorageReader` interface. It integrates with storage read flows that need full-buffer semantics despite underlying GCS readers returning smaller chunks.

## Risks and Test Signals
`io.ReadFull` changes normal `Read` behavior: callers requesting a large buffer may block until the buffer fills or EOF/error occurs. This is correct for call sites expecting full responses but risky for streaming consumers that rely on partial reads. The EOF conversion is intentional compatibility behavior and is covered by `full_read_closer_test.go`.
