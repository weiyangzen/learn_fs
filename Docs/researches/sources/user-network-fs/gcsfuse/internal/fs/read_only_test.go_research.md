<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/read_only_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/read_only_test.go

Purpose: confirms that a read-only mount rejects mutating operations while preserving bucket contents.

Important APIs/types/functions: ogletest suite `ReadOnlyTest`; `SetUpTestSuite` sets `t.mountCfg.ReadOnly = true`; tests `CreateFile`, `ModifyFile`, and `DeleteFile`.

Control flow: the suite mounts read-only, attempts local file creation, opening an existing GCS object for read/write, and removing an existing GCS object through the mount. Each operation must return an error containing `read-only`.

State and persistence behavior: fake GCS objects are the authoritative persistent state. `DeleteFile` reads the object after the failed unlink to prove the bucket was not mutated.

Dependencies and integration points: depends on mount-level read-only enforcement before write paths such as create, open-for-write, and unlink reach object mutation. Uses `storageutil.CreateObject` and `ReadObject` for out-of-band validation.

Risks: `ModifyFile` calls `f.Close()` even when `os.OpenFile` fails, which assumes the returned file value is safe in the runtime path. The important behavioral risk is any write path bypassing the read-only mount guard.

Test signals: creation, modification, and deletion all fail with read-only errors, and GCS object content remains unchanged after deletion attempt.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/read_only_test.go -->
