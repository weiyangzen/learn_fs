# sources/storage-engines/pebble/sstable/blob/rewrite.go

## Purpose
This file implements `FileRewriter`, which copies a live subset of values from an input blob file into a new blob file while preserving compatibility with existing handles.

## Important APIs, Types, and Functions
`FileRewriter` stores the original blob file ID, an output `FileWriter`, and an input `ValueFetcher`.

`NewFileRewriter` creates the writer, initializes a fetcher over a single input file mapping, and accepts output file number, writable, and writer options.

`CopyBlock` copies selected value IDs from one original block ID into the output file, preserving ascending block order and adding virtual block mappings.

`Close` closes the output writer and input fetcher, combining errors.

`inputFileMapping` implements `base.BlobFileMapping` by always returning the same input object.

## Control Flow
`CopyBlock` sorts requested value IDs. If pending output values plus the next block's total value size exceed the flush governor, it flushes before starting so all copied values for one original block remain in one physical block. It records a virtual block mapping from original block ID to current physical block and value offset. It skips duplicate value IDs, fills internal gaps with nil values to preserve value-ID indexing, fetches each referenced value from the original file, rejects empty copied values, and appends it to the output block.

## State and Persistence Behavior
The output blob file persists only live values plus nil placeholders for sparse gaps inside copied virtual blocks. The index block's virtual mapping allows old handles to resolve into the rewritten file. The rewriter does not persist liveness metadata itself; callers provide the value IDs to retain.

## Dependencies and Integration Points
It depends on blob `FileWriter`, `ValueFetcher`, objstorage writable, block read environment, base object info, and blob index virtual mapping semantics. It is intended for value-separation garbage collection or blob-file compaction.

## Risks
`CopyBlock` must be called with ascending block IDs; the encoder enforces ordering through virtual mapping assertions. Duplicate value IDs are tolerated due to missing per-SSTable liveness data, but this is a workaround. Empty values are rejected, so callers must not request handles that legitimately point to empty blob values. Incorrect `totalValueSize` can produce suboptimal or invalid block grouping decisions.

## Test Signals
Direct tests are not listed here, but blob writer sparse tests and fetcher retrieval tests exercise the core virtual mapping and handle-preservation mechanisms used by rewriter output.
