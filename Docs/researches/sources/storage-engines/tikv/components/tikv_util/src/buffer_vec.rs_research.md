# sources/storage-engines/tikv/components/tikv_util/src/buffer_vec.rs

Purpose: implements `BufferVec`, a vector-like container storing many logical byte buffers in one contiguous `Vec<u8>` plus an offsets array, reducing allocation overhead for collections of byte slices.

Important APIs: constructors `new()` and `with_capacity()`, capacity/length accessors, `push`, `concat_extend`, `begin_concat_extend`, `pop`, `last`, `shift`, `truncate`, `clear`, `copy_from`, `copy_n_from`, `retain_by_array`, `iter`, indexing, and `Extend` implementations. `WithConcatExtend` appends multiple pieces as one logical buffer and implements `codec::prelude::BufferWriter`. `Iter` is an exact-size iterator over logical buffers.

Control flow: each logical buffer starts at an offset in `offsets`; the end is the next offset or `data.len()`. `shift()` drains data before the nth offset and subtracts the removed data offset from remaining offsets. `truncate()` cuts data at the nth offset. `retain_by_array()` compacts retained buffers in place using unsafe pointer copies and then resets vector lengths.

State and persistence: state is purely in-memory `data` and `offsets`. Empty buffers are represented by repeated offsets, so zero-length items are preserved.

Dependencies and integration: uses `codec::prelude::BufferWriter` for direct buffer writes and `log_wrappers::Value` for debug formatting. It is suitable for batching encoded keys/values without per-entry allocation.

Risks: unsafe compaction in `retain_by_array()` depends on valid offset invariants and a sufficiently long retain array. `begin_concat_extend()` creates an empty logical buffer even if no data is written. `Index` panics out of bounds.

Test signals: local tests extensively cover empty buffers, push/pop/shift/truncate, copy variants, retention combinations, iterator behavior, debug formatting, and extend semantics.
