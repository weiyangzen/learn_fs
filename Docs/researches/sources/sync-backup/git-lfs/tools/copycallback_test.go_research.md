<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/copycallback_test.go -->
# sources/sync-backup/git-lfs/tools/copycallback_test.go

Purpose: unit tests for callback reader progress accounting.

Important APIs/types/functions: tests `CallbackReader.Read`, `BodyWithCallback.Read`, `BodyWithCallback.Seek`, and helper `EOFReader`.

Control flow: a custom `EOFReader` returns bytes with `io.EOF`; tests ensure callbacks still fire when bytes are read with EOF. Additional tests verify byte-body read size increments and seek modes update internal progress to start/current/end offsets.

State and persistence: in-memory byte slices and counters only.

Dependencies and integration points: uses `testify/assert`; validates progress accounting used by transfer code.

Risks: tests do not cover callback error propagation, nil callback reset behavior, or file-backed bodies.

Test signals: covers underfilled EOF callback, EOFReader behavior, cumulative reads, and seek bookkeeping.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/copycallback_test.go -->
