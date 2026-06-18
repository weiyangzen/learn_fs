# sources/storage-engines/pebble/sstable/colblk/value_liveness_block_test.go

## Purpose
Datadriven coverage for reference liveness block encoding and debug formatting.

## Important APIs, Types, and Functions
- `TestValueLivenessBlock` runs `testdata/value_liveness_block`.
- `build` command initializes an encoder, adds one liveness value per input line using the line number as reference ID, finishes, decodes, and returns `DebugString`.

## Control Flow
Input lines are split into fields, the first field becomes the encoded value, rows are added densely, and the decoder immediately reads the resulting bytes to verify structure through formatted output.

## State and Persistence Behavior
The test exercises the dense row/reference-ID contract and checks the exact columnar block representation via `DebugString`.

## Dependencies and Integration Points
Uses `datadriven`, string parsing, and the production encoder/decoder.

## Risks and Edge Cases
The test focuses on layout formatting, not semantic decoding of blob liveness bitmaps. Malformed input lines would panic due to field indexing.

## Test Signals
Useful regression signal for header, raw bytes column encoding, and debug description stability.
