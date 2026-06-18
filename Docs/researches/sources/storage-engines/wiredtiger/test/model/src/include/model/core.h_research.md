# sources/storage-engines/wiredtiger/test/model/src/include/model/core.h

Purpose: foundational model constants, aliases, and exception types.

Important APIs and types: defines `timestamp_t`, `txn_id_t`, and `write_gen_t`; constants for none/latest/max timestamps, none/max transaction IDs, and write generation bounds; and exception classes `model_exception`, `wiredtiger_exception`, `wiredtiger_abort_exception`, and `known_issue_exception`. It mirrors public/internal WiredTiger values such as `WT_TS_MAX`, `WT_TS_NONE`, and `WT_TXN_NONE`, with static assertions where headers allow.

Control flow and state: header-only type and constant definitions, no mutable state. `wiredtiger_exception` captures a WiredTiger error code and formats messages through session or global WiredTiger strerror functions. `known_issue_exception` stores a ticket identifier.

Dependencies and integration: includes `wiredtiger.h` and standard exception/string/limits headers. `core.cpp` completes the `WT_TXN_MAX` assertion using internal headers. Every model core and driver file depends on these definitions.

Risks and test signals: constants must stay aligned with WiredTiger internals or MVCC/recovery modeling becomes invalid. Non-thread-safe `wiredtiger_exception` constructors that use global strerror are documented. Compile-time assertions are the main drift signal.
