# sources/storage-engines/pebble/sstable/runlength_bitmap_test.go

## Purpose
Validates the run-length bitmap encoder/decoder with datadriven expected encodings and randomized round trips.

## Important APIs, Types, And Functions
`TestRunLengthBitmap` reads `testdata/runlength_bitmap`, encodes textual `0`/`1` inputs, reports `Size`, dumps binary encoding with `binfmt.FHexDump`, and verifies decode/re-encode equality. `TestRunLengthBitmap_Randomized` generates random bitmap densities and validates canonical round trips.

## Control Flow And State
The datadriven test resets a reusable encoder and buffers for each command, sets bits for `1` characters in the input, finalizes the encoding, then reconstructs a new encoder by iterating `IterSetBitsInRunLengthBitmap`. The randomized test chooses bitmap length up to 100,000 and a density cutoff, encodes all selected indexes in order, and requires the re-encoded bytes to match exactly.

## Persistence And Integration
No durable files are written beyond datadriven test output expectations. The tests integrate with the public encoder and iterator in `runlength_bitmap.go`.

## Risks
The tests do not feed malformed encodings or out-of-order `Set` calls. Randomized coverage uses a time-based seed without logging it, which can make failures harder to reproduce.

## Test Signals
The combination of exact datadriven cases and randomized canonicalization gives useful signal that `Size`, `FinishAndAppend`, and the sequential decoder agree on the encoding format.
