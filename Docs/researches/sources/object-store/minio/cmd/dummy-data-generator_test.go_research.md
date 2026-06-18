<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/dummy-data-generator_test.go -->
## sources/object-store/minio/cmd/dummy-data-generator_test.go

Purpose: This test helper file defines a deterministic repeating data generator and reader comparison utility used by tests that need predictable stream content without storing large fixtures.

Important APIs and types: `alphabets` is the repeating byte alphabet. `DummyDataGen` implements `io.ReadSeeker` with an internal repeated byte slice, current index, and total length. `NewDummyDataGen(totalLength, skipOffset)` constructs a finite reader over the infinite repeated alphabet stream, optionally starting at an offset. `(*DummyDataGen).Read` fills caller buffers until the configured length and returns `io.EOF` at the end. `(*DummyDataGen).Seek` supports start/current/end seeking with negative-position validation. `cmpReaders` compares two readers in 32 KiB chunks using `io.ReadFull`.

Control flow: Construction validates non-negative length and offset, normalizes the skip offset by the alphabet length, repeats the alphabet 100 times, and slices enough bytes to avoid wrapping during normal reads. Read loops copy from the repeated slice modulo its length until either the caller buffer is full or the logical length is reached, correcting over-read counts at EOF. Seek adjusts `idx` based on `whence` and rejects negative target positions. `cmpReaders` reads both readers chunk-by-chunk, compares byte counts and contents, and treats matching EOF or unexpected EOF on both readers as a clean end.

State and persistence behavior: State is in-memory only. The important invariant is stream composability: a full stream can equal the concatenation of shorter streams with matching offsets.

Dependencies and integration points: It depends on `bytes`, `errors`, `fmt`, `io`, and `testing`. It is located in a `_test.go` file, so it is test-only support for package `cmd`.

Risks: `Read` returns `len(p)` at the end of the non-EOF path, not the accumulated `n`; given the loop structure this is normally equivalent when the buffer is filled, but it is a subtle implementation detail. The fixed `multiply = 100` assumes the internal repeated slice is large enough for modulo-slice copy behavior; very large reads still work through modulo reuse, but construction is less direct than a simple modulo copy loop. `Seek` does not reject unknown `whence` values and returns the current index unchanged.

Test signals: `TestDummyDataGenerator` checks zero-length reads, offset normalization, composability, and seeking by one alphabet length. `TestCmpReaders` verifies equal small readers compare true and length-mismatched readers compare false.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/dummy-data-generator_test.go -->
