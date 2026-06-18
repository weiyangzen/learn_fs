# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/stream.h

## Purpose

`stream.h` defines RapidJSON's stream concept and provides the basic string-backed streams used by the reader and writer. It is the small abstraction layer that lets parsing and writing operate over memory buffers, encoded streams, file streams, and custom user streams with the same API.

## Important APIs and Types

The stream concept requires `Ch`, `Peek`, `Take`, `Tell`, `PutBegin`, `Put`, `Flush`, and `PutEnd`, though read-only and write-only streams only implement the subset they need. `StreamTraits<Stream>::copyOptimization` lets the reader make local stream copies for cheap-copy streams. Utility functions `PutReserve`, `PutUnsafe`, and `PutN` support generic and specialized output paths. `GenericStringStream<Encoding>` is a read-only string stream, `StringStream` is its UTF-8 alias, `GenericInsituStringStream<Encoding>` is a read-write in-situ parsing stream, and `InsituStringStream` is its UTF-8 alias.

## Control Flow

`GenericStringStream` advances a `src_` pointer on `Take`, returns `*src_` on `Peek`, and computes offsets relative to `head_`. Its write methods assert because it is read-only. `GenericInsituStringStream` reads from `src_`, writes through `dst_` after `PutBegin`, and uses `PutEnd` to report bytes written; `Push` and `Pop` let parsers reserve or roll back decoded output. `PutN` reserves capacity when possible and emits repeated characters with `PutUnsafe`.

## State and Persistence

String streams only hold raw pointers into caller-owned memory. They do not allocate or own buffers. In-situ streams mutate the supplied input buffer during parsing and maintain separate read and write cursors. `StreamTraits` marks both string stream variants as safe for local copy optimization.

## Dependencies and Integration Points

The header includes `rapidjson.h` and `encodings.h`. `reader.h` depends on these streams for normal and in-situ parsing, `writer.h` and `stringbuffer.h` consume the stream utility functions, and users can specialize `StreamTraits` plus `PutReserve`/`PutUnsafe` for custom streams.

## Risks and Edge Cases

`GenericStringStream` assumes the input has a readable terminator; it performs no bounds checks. Calling write methods on read-only streams or `Put` before `PutBegin` on in-situ streams is an assertion failure, not a recoverable runtime error. Because streams borrow external storage, lifetime and mutability are the caller's responsibility.

## Test Signals

Tests should cover `Peek`/`Take`/`Tell` offsets, local copy optimization behavior in reader paths, in-situ `PutBegin`/`Put`/`PutEnd` mutation, `Push`/`Pop` cursor changes, `PutN` output with specialized streams, and custom stream trait specialization.
