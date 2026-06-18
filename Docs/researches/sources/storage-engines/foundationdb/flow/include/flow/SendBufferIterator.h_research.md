<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/SendBufferIterator.h -->
# sources/storage-engines/foundationdb/flow/include/flow/SendBufferIterator.h

Purpose: This header declares an iterator adapter that exposes Flow `SendBuffer` chains as Boost.Asio `const_buffer` values for socket writes.

Important APIs and types: `SendBufferIterator` stores a `SendBuffer const*` and a byte or segment limit. It declares standard forward-iterator aliases, equality/inequality, prefix increment, and dereference returning `boost::asio::const_buffer`.

Control flow: Iteration starts from a `SendBuffer` pointer and advances through implementation-defined buffer links until null or the configured limit is reached. Dereference converts the current send-buffer slice into an Asio buffer.

State and persistence behavior: State is transient pointer iteration over send buffers. No persistence is involved; correctness depends on the underlying `SendBuffer` memory remaining alive during Asio write setup.

Dependencies and integration points: It depends on Flow serialization types for `SendBuffer` and Boost.Asio. It is part of the network write path that passes serialized message buffers to Asio without copying.

Risks: Iterator validity is tied to the send-buffer chain lifetime. Limit handling is implemented out of line, so boundary tests are important. The iterator's `reference` and `pointer` aliases name buffer references/pointers even though `operator*` returns by value, which is acceptable for Asio use but not a full STL iterator contract.

Test signals: Tests should cover empty iterators, multi-buffer chains, limit truncation, Asio buffer size/address correctness, and equality after incrementing to the end.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/SendBufferIterator.h -->
