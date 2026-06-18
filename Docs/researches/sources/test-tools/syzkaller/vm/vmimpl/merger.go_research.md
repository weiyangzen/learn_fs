# sources/test-tools/syzkaller/vm/vmimpl/merger.go

Purpose: merges multiple VM output streams, preserves output type metadata, optionally tees complete lines, and reports reader errors to command lifecycle code.

Important APIs/types/functions: `OutputType`, `Chunk`, `MergerError`, `OutputMerger`, `NewOutputMerger`, `Wait`, `Errors`, `Add`, `AddDecoder`, and `runDecoder`.

Control flow: each added reader gets a goroutine that reads 4 KiB chunks. If a protocol decoder is supplied, decoded payloads are emitted separately. Raw output is buffered until the last newline, then cloned and sent as a `Chunk`; incomplete trailing data is newline-terminated on read error. `Errors(ctx)` creates an errgroup waiting for active decoders to finish and returns the first non-nil `MergerError`. `Wait` waits for all decoders and closes the public output channel.

State and persistence: state is in memory: output channel, per-name decoder state, wait group, pending buffers, and optional tee writer lock. No files are written except through the caller-provided tee.

Dependencies and integration: used by VM backends to combine console, stdout, and stderr for the high-level monitor and by `vmimpl.Multiplex` to detect EOF/failure.

Risks: `Add` with an existing name replaces error state while old goroutine may still run; output sends are lossy under backpressure due to default case; error is always wrapped, including expected EOF; decoders must return valid slice indexes.

Test signals: `merger_test.go` covers incomplete-line buffering, tee ordering, EOF errors, persistent error reporting, replacing decoder state by name, and hanging background readers.
