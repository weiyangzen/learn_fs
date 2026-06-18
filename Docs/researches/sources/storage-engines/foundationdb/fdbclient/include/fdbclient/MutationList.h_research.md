# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/MutationList.h

## Purpose
Defines an arena-backed, append-friendly, forward-iterable representation of ordered mutations. It is optimized for O(1) deserialization and efficient serialization/append in commit-related paths.

## Important APIs, Types, And Functions
`MutationListRef` stores a linked list of `Blob` chunks. Each blob's `StringRef` contains one or more serialized mutation records in the layout `Header(type, p1len, p2len)`, followed by param1 bytes and param2 bytes. `Header` size is asserted to match `MutationRef::OVERHEAD_BYTES`. `Iterator` decodes the current record into a `MutationRef` and advances across blob boundaries. Constructors support empty lists and deep copy into an arena. `push_back_deep()`, `append_deep()` overloads, `serialize_load()`, `serialize_save()`, and `allocate()` implement mutation insertion and serialization.

## Control Flow
Appending allocates a header plus payload in the arena, writes type and parameter lengths, copies parameter bytes, and extends or creates the active blob. Iteration decodes the header at the current pointer and increments to the next header or next blob. Deserialization reads total bytes and creates one zero-copy blob from the arena reader. Serialization writes total bytes, then raw blob data in order.

## State And Persistence Behavior
State is in-memory inside an `Arena`, with linked blobs and a `totalBytes` counter. Serialized form is durable/transmittable as total byte count plus concatenated mutation bytes. The deep-copy constructor and append methods copy payload bytes, while deserialization can be zero-copy relative to the arena.

## Dependencies And Integration Points
The header depends on FDB types and commit transaction mutation definitions. It is used by commit proxy/client transaction machinery, and the comment notes a commit-proxy reimplementation of `serialize_save()` that includes yielding.

## Risks And Test Signals
Risks include corrupt header lengths, iterator advancement past blob boundaries, arena allocation assumptions when extending blobs, integer truncation for large payloads, and divergence from the commit-proxy serialization copy. Test signals should include empty/non-empty lists, multi-blob iteration, deep copy independence, serialization/deserialization round trips, large mutation payloads, malformed input rejection/assertions, and compatibility with commit transaction mutation encoding.
