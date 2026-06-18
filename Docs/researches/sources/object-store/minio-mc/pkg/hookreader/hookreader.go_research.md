## sources/object-store/minio-mc/pkg/hookreader/hookreader.go

Purpose: wraps a source `io.Reader` and a hook reader so each successful source read is mirrored to the hook, commonly for progress accounting. Important APIs are `hookReader`, `Read`, `Seek`, and `NewHook`.

Control flow reads from the source, returns non-EOF source errors immediately, then calls `hook.Read` with the exact bytes read and returns non-EOF hook errors. `Seek` delegates to the source if it implements `io.Seeker`, otherwise to the hook if it does. State is the two readers. Dependencies are only `io`. Risks include the hook being modeled as a reader rather than writer, partial hook reads not being validated, EOF treatment that may hide hook completion, and `Seek` not coordinating both readers. `hookreader_test.go` covers basic progress byte counting.
