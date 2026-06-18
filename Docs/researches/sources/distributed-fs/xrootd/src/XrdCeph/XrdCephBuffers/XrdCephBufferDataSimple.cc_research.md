# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/XrdCephBufferDataSimple.cc

Purpose: implements a `std::vector<char>` backed buffer data object for Ceph buffering.

Important APIs/types/functions: static global memory counters; constructor/destructor; capacity/length/valid/offset accessors; `invalidate`; `readBuffer`; `writeBuffer`; raw accessors are inline in the header.

Control flow: construction allocates a zero-filled vector and marks the buffer valid. `readBuffer` validates state and bounds, copies up to available data from internal offset to caller buffer, and returns bytes copied. `writeBuffer` validates bounds, copies bytes into the internal vector at local offset, updates external offset, length, and validity.

State and persistence: stores buffer size, validity, vector memory, external offset, valid length, per-object counters, and static aggregate memory counters. No persistence outside memory.

Dependencies and integration points: uses `Timer_ns` and `BUFLOG`; implements `IXrdCephBufferData` for the simple algorithm and raw adapters.

Risks: destructor `clear` plus `reserve(0)` does not guarantee memory release; `shrink_to_fit` would be clearer if immediate release matters. Constructor marks an empty buffer valid, though length is zero. Timing counters are declared but not updated. `writeBuffer` external offset may be redundant/inconsistent with algorithm tracking.

Test signals: construct/destruct memory counters, zero capacity raw pointer, read invalid buffer, read beyond length, write bounds failures, length growth after writes, and invalidate reset.
