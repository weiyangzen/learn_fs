## sources/user-network-fs/gcsfuse/internal/util/file_util_test.go

Purpose: Tests conversion from generic open flags to `OpenMode`.

Important APIs/types/functions: `mockOpenFlags` implements `OpenFlagAttributes`; `TestFileOpenMode` covers read-only, write-only, read-write, append, direct, and combined flags.

Control flow: each case constructs mock booleans, calls `FileOpenMode`, and compares to `NewOpenMode`.

State and persistence behavior: no state.

Dependencies and integration points: validates the abstraction used to avoid importing FUSE internal flag types.

Risks: does not test inconsistent flag combinations such as read-only and write-only both true, where production priority matters.

Test signals: good nominal coverage of all exported file-mode bits.
