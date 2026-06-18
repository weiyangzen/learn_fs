## sources/storage-engines/pebble/sstable/colblk/bitmap_test.go

Purpose: Tests columnar bitmap encoding, binary formatting, fixed and randomized seek behavior for set/unset bits, inversion, and builder performance.

Important APIs/types/functions: `TestBitmapFixed`, `TestNextPrevBitInWord`, `dumpBitmap`, `TestBitmapRandom`, and `BenchmarkBitmapBuilder`.

Control flow: The fixed datadriven test builds bitmaps from textual 0/1 input, optional row/offset arguments, optional inversion, validates `Size`/`InvertedSize`/`Finish` offsets, decodes the bitmap, dumps bits, and prints binary layout through `bitmapToBinFormatter`. It also runs seek commands against the last built bitmap. The bit primitive test reconstructs random words by repeatedly calling next/prev helpers. The randomized test builds boolean arrays for fixed and random sizes/probabilities, optionally inverts, decodes, checks every `At`, and verifies set/unset predecessor/successor correctness by scanning gaps.

State and persistence behavior: Tests encoded byte layout, padding with nonzero offsets, all-zero/default encodings, summary table correctness, and tail truncation when builder writes beyond requested row count.

Dependencies and integration points: Uses `datadriven`, `binfmt`, `treeprinter`, `math/rand/v2`, `time`, `unicode`, and `require`.

Risks: Randomized tests seed from current time and log the seed, so failures are reproducible only if logs are available. The benchmark allocates a fresh builder per iteration and may not isolate builder reuse behavior.

Test signals: Strong coverage for correctness of bitmap search primitives, encoded structure, inversion, sparse/dense probabilities, row counts around word boundaries, and offsets.
