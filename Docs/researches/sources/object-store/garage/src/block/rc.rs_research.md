# sources/object-store/garage/src/block/rc.rs

Purpose: implements local block reference-count storage and repair recalculation hooks.

Important APIs/types/functions: `CalculateRefcount`, `BlockRc`, `block_incref`, `block_decref`, `get_block_rc`, `clear_deleted_block_rc`, `recalculate_rc`, and internal `RcEntry::{Present, Deletable, Absent}` with parse/serialize/increment/decrement/state helpers.

Control flow: increments parse current DB entry and write a positive count. Decrements transition count 1 to `Deletable` with timestamp `now + BLOCK_GC_DELAY`; already zero states remain unchanged. `recalculate_rc` runs registered callbacks inside a DB transaction, compares calculated count to stored count, and writes either `Present` or delayed `Deletable`.

State and persistence: RC entries live in the `block_local_rc` tree. Format is 8-byte big-endian count for present, or 16 bytes with a zero prefix and deletion timestamp for deletable, preserving compatibility with older zero-count semantics.

Dependencies and integration points: uses `garage_db::Tree` and transactions, `arc_swap::ArcSwapOption` to publish recalculation callbacks, `garage_util::data::Hash`, and time helpers. `BlockManager` invokes it during metadata mutations, resync, repair, and admin block info.

Risks: invalid RC byte lengths panic with a corruption message. Decrementing an absent/deletable entry is idempotent rather than underflowing, which avoids crashes but can hide caller mistakes. Recalculation is unavailable until higher layers register callbacks, so early repair calls can fail.

Test signals: no direct tests here; DB test suite covers transaction mechanics, while block repair/resync integration should cover RC transitions and recalculation.
