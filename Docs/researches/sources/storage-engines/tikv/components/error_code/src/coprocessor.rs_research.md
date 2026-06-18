<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/error_code/src/coprocessor.rs -->
# sources/storage-engines/tikv/components/error_code/src/coprocessor.rs

Purpose: this module provides stable coprocessor error codes under `KV:Coprocessor:` for request execution, expression evaluation, encoding, storage interaction, and quota errors.

Important APIs and constants: constants include request/control failures such as `LOCKED`, `DEADLINE_EXCEEDED`, `MAX_PENDING_TASKS_EXCEEDED`, and `MEMORY_QUOTA_EXCEEDED`; expression/data failures such as `INVALID_DATA_TYPE`, `ENCODING`, `COLUMN_OFFSET`, `UNKNOWN_SIGNATURE`, `EVAL`, `CORRUPTED_DATA`, and `INVALID_CHARACTER_STRING`; storage-related failures such as `STORAGE_ERROR`, `DEFAULT_NOT_FOUND`, and `INVALID_MAX_TS_UPDATE`. `ALL_ERROR_CODES` is generated.

Control flow and state: declarative constants only. No direct conversion implementation is present.

Dependencies and integration points: this namespace is for TiKV coprocessor code that evaluates pushed-down SQL expressions and reads MVCC data. The generator binary includes it in the TOML catalog.

Risks: all descriptions and workarounds are empty. The list contains both user-input/data issues and internal storage issues; downstream mapping must preserve that distinction for actionable responses.

Test signals: no module-local tests exist. Compilation validates macro expansion.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/error_code/src/coprocessor.rs -->
