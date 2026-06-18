# sources/sync-backup/kopia/internal/gather/gather_write_buffer_test.go

Purpose: tests append, section extraction, allocator selection, and large-buffer chunking behavior for `WriteBuffer`.

Important APIs/types/functions: `NewWriteBuffer`, `WriteBuffer.Append`, `Write`, `ToByteSlice`, `Length`, `AppendSectionTo`, `Reset`, `MakeContiguous`, `NewWriteBufferMaxContiguous`, and `Bytes`.

Control flow: `TestGatherWriteBuffer` appends strings and repeated bytes across chunk boundaries, checks slice counts, extracts a section, and resets. `TestGatherDefaultWriteBuffer` verifies lazy default allocation. Contiguous tests assert small and mid-size lengths choose the expected allocator while over-max lengths use raw allocation. The max-contiguous test writes millions of small chunks and verifies slice counts grow by 16MB-sized chunks.

State/persistence behavior: in-memory buffer state is closed with defer in most tests. The tests inspect package internals because they are in package `gather`.

Dependencies/integration: exercises `fmt.Fprintf` through the `io.Writer` implementation and internal allocator globals.

Risks/test signals: tests protect allocator selection thresholds and chunk-boundary behavior. Very large append loops can be somewhat expensive but directly validate high-volume behavior.
