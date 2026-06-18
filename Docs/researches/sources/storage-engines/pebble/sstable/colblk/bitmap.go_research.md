## sources/storage-engines/pebble/sstable/colblk/bitmap.go

Purpose: Implements a compact columnar boolean bitmap with optional all-zero encoding, 64-bit-word storage, summary words for fast set-bit predecessor/successor searches, a builder, and debug formatting.

Important APIs/types/functions: `Bitmap`, `DecodeBitmap`, `At`, `SeekSetBitGE`, `SeekSetBitLE`, `SeekUnsetBitGE`, `SeekUnsetBitLE`, `BitmapBuilder`, `Set`, `Reset`, `Size`, `InvertedSize`, `Invert`, `Finish`, `bitmapRequiredSize`, `bitmapToBinFormatter`, `nextBitInWord`, and `prevBitInWord`.

Control flow: Decoding reads a one-byte encoding tag. Zero encoding returns a nil-data bitmap; default encoding aligns to 8 bytes, computes required size, and builds an unsafe uint64 decoder over bitmap words plus summary words. Set-bit searches check the current word first, then use summary words to jump to the next/previous nonzero primary word. Unset-bit searches scan primary words for non-`MaxUint64`. Builder tracks words and `minNonZeroRowCount`; `Finish` writes encoding, padding, primary words truncated to row count, zeroes sparse tail words, masks extra bits past `nRows`, and writes summary words.

State and persistence behavior: Encoded layout is one tag byte, optional padding to 8-byte alignment, primary bitmap words, then summary words. Zero bitmaps use only the tag byte. Deterministic padding and tail-bit masking protect stable on-disk bytes and correct summary search behavior.

Dependencies and integration points: Implements `Array[bool]` and `ColumnWriter`; `DecodeBitmap` implements `DecodeFunc[Bitmap]`. Depends on `unsafeUint64Decoder`, `makeUintsEncoder`, `binfmt`, `treeprinter`, `invariants`, and low-level colblk alignment helpers.

Risks: Several methods rely on caller bounds per comments; invariant checks may be disabled. `DecodeBitmap` panics on short buffers rather than returning an error. `SeekSetBitGE` can return an index beyond `bitCount` if extra tail bits were not masked by the builder, making writer correctness critical. `prevBitInWord` is called with unsigned bit arithmetic, so callers must avoid underflow cases.

Test signals: `bitmap_test.go` provides fixed datadriven binary/seek tests, randomized probability/inversion tests over many sizes, bit primitive reconstruction tests, and a builder benchmark.
