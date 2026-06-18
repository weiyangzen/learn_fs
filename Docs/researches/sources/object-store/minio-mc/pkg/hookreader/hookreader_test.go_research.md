## sources/object-store/minio-mc/pkg/hookreader/hookreader_test.go

Purpose: gocheck-based unit test for the hookreader progress behavior.

Control flow creates a buffer containing `Hello`, a `customReader` that counts the length of every buffer it receives, wraps both with `NewHook`, reads three bytes, and asserts the source returned three bytes while progress counted three. State is local buffers and a counter. Dependencies are `testing`, `bytes`, and `gopkg.in/check.v1`. Test signal is basic but narrow: it does not test nil hook passthrough, source or hook errors, EOF behavior, partial reads, or `Seek`. It confirms the intended integration contract for progress bars.
