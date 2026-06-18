# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/set.rs

Purpose: represents MySQL `SET` values as a bitmap plus shared string table.

Important APIs/types/functions: owned `Set`, borrowed `SetRef<'a>`, constructors `Set::new` and `SetRef::new`, `value`, `as_ref`, `to_owned`, `is_set`, `is_empty`, `Display`, ordering/equality, and `AsMySqlBool`.

Control flow: display iterates all labels in `BufferVec`, appending comma-separated labels whose bit is set in `value`. Equality and ordering compare only the numeric bitmap. `AsMySqlBool` returns true when any bit is set.

State and persistence: `Set` owns `Arc<BufferVec>` plus `u64` bitmap; `SetRef` borrows the buffer. There is no persistence. TiDB guarantees no more than 64 set members, matching the bitmap width.

Dependencies and integration points: uses `tikv_util::buffer_vec::BufferVec` for compact label storage and integrates with codec boolean conversion.

Risks: `is_set` shifts `1 << idx`; callers must keep indexes below 64. Equality ignores label table identity, so two sets with the same bitmap but different labels compare equal. Display uses lossy UTF-8 conversion. Tests cover string rendering, bit membership, and empty checks.
