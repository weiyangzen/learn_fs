# sources/storage-engines/pebble/sstable/blob/blob_test.go

## Purpose
This file tests blob file writing, reader footer/properties inspection, sparse virtual-block layouts, writer stats, compression counters, and inline handle encode/decode round trips.

## Important APIs, Types, and Functions
`TestBlobWriter` supports datadriven `build`, `build-sparse`, and `open` commands. It uses `scanFileWriterOptions` to parse target block size, threshold, compression, and format.

`printFileWriterStats` renders writer stats and compression counters.

`TestHandleRoundtrip` encodes `InlineHandle`, decodes preface and suffix, and compares the results.

## Control Flow
`build` creates a memory object, writes each input line as a blob value, prints handles, closes the writer, and prints stats. `build-sparse` also interprets flush and virtual-block marker lines to force sparse/rewritten-style layouts. `open` creates a `FileReader`, prints footer fields and properties, then closes it.

## State and Persistence Behavior
The in-memory object persists between `build` and `open` commands within a datadriven run. Writer options decide format and compression behavior.

## Dependencies and Integration Points
Tests use `objstorage.MemObj`, blob writer/reader APIs, block compression profiles, datadriven input, and handle encode/decode from `handle.go`.

## Risks
Golden output is sensitive to compression, block-size thresholds, footer format, stats accounting, and handle string formatting. `build-sparse` reaches into writer internals, so refactoring may require test updates.

## Test Signals
Stable handles, stats, compression counters, footer fields, property text, and handle roundtrip equality signal correctness across writer, reader, and handle encoding.
