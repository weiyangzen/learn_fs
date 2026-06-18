## sources/user-network-fs/gcsfuse/internal/util/file_util.go

Purpose: Represents FUSE file open modes and converts FUSE open flag abstractions into internal access/behavior flags.

Important APIs/types/functions: access constants `ReadOnly`, `WriteOnly`, `ReadWrite`; file flags `O_APPEND`, `O_DIRECT`; `OpenMode`; `NewOpenMode`; accessors; `IsAppend`; `IsDirect`; `OpenFlagAttributes`; `FileOpenMode`.

Control flow: access mode priority is read-only, then write-only, otherwise read-write. File flags OR append/direct bits. Append is considered active only for non-read-only modes.

State and persistence behavior: pure value logic, no persistence.

Dependencies and integration points: decouples gcsfuse logic from concrete `jacobsa/fuse` internal flag types and feeds metrics/write-mode decisions.

Risks: if a flag object reports inconsistent access booleans, read-only wins silently. `IsReadWrite` is not directly checked except by fallback behavior.

Test signals: `file_util_test.go` covers access modes and append/direct combinations.
