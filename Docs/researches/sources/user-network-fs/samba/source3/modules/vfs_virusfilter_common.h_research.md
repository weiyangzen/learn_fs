# sources/user-network-fs/samba/source3/modules/vfs_virusfilter_common.h

## Purpose
This header defines the shared data model and backend ABI for the Samba virusfilter VFS module family. It is the contract between the core VFS frontend, scanner backends, and utility layer.

## Important APIs, Types, and Functions
`virusfilter_action` describes remediation choices: do nothing, quarantine, rename, and delete. `virusfilter_result` describes scan outcomes: OK/init success, clean, error, infected, and suspected. `struct virusfilter_config` carries all share configuration and runtime state, including scan policy, archive/mime options, size limits, exclude/infected name lists, result cache, remediation commands and errnos, quarantine/rename strings, socket path, I/O handle, and selected backend. `struct virusfilter_backend_fns` declares optional `connect`, `disconnect`, `scan_init`, `scan`, and `scan_end` callbacks. `struct virusfilter_backend` names a backend, carries optional version/private data, and points to the callback table. The header declares init functions for Sophos, F-Secure, ClamAV, and dummy backends.

## Control Flow
The core module fills `virusfilter_config`, calls exactly one backend init function, then drives backend callbacks through the function table. Backends may allocate private state under `backend_private` during connect and may use the shared `io_h`.

## State and Persistence
The header itself has no persistence, but its structures define all in-memory virusfilter state. `virusfilter_config` is per VFS handle/share connection. `cache`, `io_h`, and `backend` are owned by talloc hierarchy. External persistence is delegated to core actions and scanners.

## Dependencies and Integration Points
It includes Samba smbd, globals, filesystem, auth, passdb, netlogon, and tsocket headers, making it a Samba-internal header rather than a standalone library ABI. It also defines and exports `virusfilter_debug_class`.

## Risks
Because backend callbacks receive the full mutable config, backends can change frontend behavior unintentionally. The `scan_init` result enum reuses scan outcomes where `VIRUSFILTER_RESULT_OK` has a special initialization meaning distinct from `CLEAN`. Any ABI change must update all backend files.

## Test Signals
Compile coverage for all backends is the main signal. API tests should verify each backend initializes `config->backend`, names itself, and supplies a valid `scan` callback.
