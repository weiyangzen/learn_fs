# sources/storage-engines/wiredtiger/test/model/src/core/core.cpp

Purpose: compile-time bridge between model constants and WiredTiger internal constants.

Important behavior: includes `model/core.h` and `wt_internal.h`, then uses `static_assert(k_txn_max == WT_TXN_MAX)` inside namespace `model`. `core.h` can assert public or locally replicated constants, but `WT_TXN_MAX` requires internal headers, so this `.cpp` performs the final check.

Control flow and state: no runtime control flow or persistent state. The file exists to fail compilation if the model's transaction maximum diverges from WiredTiger internals.

Dependencies and integration: depends on internal WiredTiger headers being available to the model library target. It integrates with the `wiredtiger_model` build as a guard against semantic drift.

Risks and test signals: if WiredTiger changes transaction ID limits, the model library stops compiling until `core.h` is updated. This is a desirable early signal because MVCC visibility and snapshot behavior depend on matching ID bounds.
