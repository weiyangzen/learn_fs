# File Research: sources/windows/winfsp/src/dll/util.c

DLL utility module for diagnostics, directory creation through `NtCreateFile`, secure named-pipe calls, module version lookup, and adaptive locking.

Diagnostic identity:
- `FspDiagIdent()` lazily derives a short identifier from the process module basename without extension, defaulting to `UNKNOWN`.

Directory creation:
- `FspCreateDirectoryFileW()` dynamically resolves `NtCreateFile` from `ntdll.dll`.
- Builds a parent-relative `OBJECT_ATTRIBUTES` using a parent directory handle.
- Forces directory create semantics via `FILE_DIRECTORY_FILE` and maps selected Win32 file flags to NT create options.
- Returns Win32-style errors through `SetLastError`.

Named-pipe security:
- `FspCallNamedPipeSecurely()` delegates to `FspCallNamedPipeSecurelyEx()`.
- Opens the pipe with identification or optional impersonation SQOS.
- Retries once after `ERROR_PIPE_BUSY` using `WaitNamedPipeW`.
- Optionally verifies pipe owner SID; small numeric `Sid` values are treated as `WELL_KNOWN_SID_TYPE`.
- Switches to message read mode and calls `TransactNamedPipe`.

Version helpers:
- `FspVersion()` caches the DLL file version MS word from version resources.
- `FspGetModuleVersion()` does the same for an arbitrary module path without global cache.
- `FspGetModuleFileName()` resolves module path, optionally combining with a relative path.

Adaptive lock:
- `FspAdaptiveLockAcquire()` always takes an SRW lock and optionally attempts a one-byte overlapped file lock at a specified offset.
- `FspAdaptiveLockRelease()` unlocks/closes the file handle if acquired and releases the SRW lock.

Notable concerns:
- `FspVersion()` is intentionally not fully thread-safe, relying on same-value resource reads and atomic 32-bit store.
- `FspCreateDirectoryFileW()` assumes non-null `SecurityAttributes` when using inherit/security fields.
