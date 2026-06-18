<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/error_code/src/storage.rs -->
# sources/storage-engines/tikv/components/error_code/src/storage.rs

Purpose: this module defines storage/MVCC/transaction error codes under `KV:Storage:`.

Important APIs and constants: general scheduler and request codes include `TIMEOUT`, `EMPTY_REQUEST`, `CLOSED`, `IO`, `SCHED_TOO_BUSY`, `GC_WORKER_TOO_BUSY`, `KEY_TOO_LARGE`, `INVALID_CF`, and `CF_DEPRECATED`. Data-format and API codes include `TTL_NOT_ENABLED`, `TTL_LEN_NOT_EQUALS_TO_PAIRS`, `PROTOBUF`, `INVALID_TXN_TSO`, `INVALID_REQ_RANGE`, `BAD_FORMAT_LOCK`, `BAD_FORMAT_WRITE`, `API_VERSION_NOT_MATCHED`, and `INVALID_KEY_MODE`. Transaction codes include `COMMITTED`, `PESSIMISTIC_LOCK_ROLLED_BACK`, `TXN_LOCK_NOT_FOUND`, `TXN_NOT_FOUND`, `LOCK_TYPE_NOT_MATCH`, `WRITE_CONFLICT`, `DEADLOCK`, `ALREADY_EXIST`, `DEFAULT_NOT_FOUND`, `COMMIT_TS_EXPIRED`, `KEY_VERSION`, `PESSIMISTIC_LOCK_NOT_FOUND`, and `COMMIT_TS_TOO_LARGE`.

Control flow and state: this is a declarative module with no local conversion implementation. It creates `ALL_ERROR_CODES` through the macro.

Dependencies and integration points: TiKV storage, transaction, scheduler, GC, API-version, flashback, and assertion paths can use these constants. The generator binary includes this module.

Risks: the large mixed namespace means downstream mapping must be precise; using `UNKNOWN` or general `IO` can obscure transaction safety issues. Descriptions and workarounds are empty despite many codes being user-actionable.

Test signals: no local tests exist beyond macro expansion during compilation.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/error_code/src/storage.rs -->
