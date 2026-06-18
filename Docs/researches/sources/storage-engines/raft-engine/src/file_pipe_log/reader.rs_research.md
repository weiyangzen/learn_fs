# sources/storage-engines/raft-engine/src/file_pipe_log/reader.rs

## Purpose
`reader.rs` provides `LogItemBatchFileReader`, a reusable, buffered, format-aware iterator over `LogItemBatch` records in one physical log file. It is used by recovery, debugging, and filtering paths to decode persisted batches without loading an entire file.

## Important APIs, Types, And Functions
`LogItemBatchFileReader<F>` tracks the current `FileId`, parsed `LogFileFormat`, optional `LogFileReader`, file size, an internal prefetch buffer, the buffer's file offset, the last valid decoded offset, and the configured read block size.

`new` initializes an unopened reader. `open` parses the log file header, records the encoded header length as the first valid offset, stores file size and reader, clears the buffer, and returns the parsed format. `reset` clears all state. `next` decodes the next `LogItemBatch` or returns `None` at EOF. `valid_offset` exposes the end of verified data for truncation decisions during recovery. `peek` is the internal buffered read and prefetch primitive.

## Control Flow
`next` loops while `valid_offset < size`. It first decodes a 16-byte `LogBatch` header at `valid_offset`. If header decoding fails and the format uses alignment, it rounds up to the next alignment and skips zero padding; non-zero padding or a still-broken aligned header becomes corruption. Once the header is decoded, it validates that the whole batch fits within the file size, builds a `FileBlockHandle` pointing to the entries block, and decodes the footer with `LogItemBatch::decode`. Successful decode advances `valid_offset` by the full batch length and returns the batch.

`peek` serves slices from the internal buffer when possible. If the requested offset is beyond the current buffer, it resets the buffer to that offset and reads at least `max(size + prefetch, read_block_size)`. If the request partially extends beyond the buffer, it appends another read. EOF is an error when fewer than required bytes are available.

## State And Persistence Behavior
The reader does not mutate files. Its key state output is `valid_offset`, which recovery uses as the truncation boundary after a corrupted tail. The `LogItemBatch::decode` call receives a `LogFileContext` built from `file_id` and parsed format version, so V2 signed checksums are verified against the physical file identity.

## Dependencies And Integration Points
It depends on `LogFileReader`, `LogFileFormat`, `is_zero_padded`, `LogBatch` header decoding, `LogItemBatch` footer decoding, `FileBlockHandle`, and `round_up`. `DualPipesBuilder::recover_queue_imp`, `debug::LogItemReader`, and `RhaiFilterMachine` all rely on its decode ordering and corruption boundaries.

## Risks And Edge Cases
If a file header is shorter than the encoded format length, `open` fails through `parse_format`. `next` treats any batch header with length beyond file size as corruption. In alignment mode it only skips zero padding when the current offset is not already aligned; corrupted padding becomes a header error. The buffering logic assumes monotonic reads within a file and debug-asserts requested offsets are not before `buffer_offset`.

## Test Signals
Reader behavior is exercised by debug-reader tests, log-batch encode/decode tests, and recovery tests that parse real files. Important signals include empty well-formed files returning `None`, corrupted files returning errors, alignment padding tolerance, checksum verification, and recovery truncation using `valid_offset`.
