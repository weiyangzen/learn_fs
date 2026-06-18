# sources/distributed-fs/xrootd/src/XrdSec/XrdSecLoadSecurity.cc

Purpose: Implements dynamic loading for the default security framework and request-protection framework, plus the client helper that creates `XrdSecProtect` objects from protocol responses.

Important APIs and functions: `XrdSecLoadSecFactory` loads `XrdSecGetProtocol`. `XrdSecLoadSecService` loads `XrdSecgetService` and optionally returns the protection singleton. `XrdSecGetProtection` validates a `kXR_protocol` response and creates client protection. `XrdSecLoadProtection` is the server-side one-time protection loader. Internal `Plug` and overloaded `Load` helpers wrap `XrdOucPinLoader`.

Control flow: The security loader defaults to `libXrdSec.so`, resolves the client factory and service factory, optionally instantiates the service with the logger/config path, and unloads on failure. The protection loader defaults to `libXrdSecProt.so` and resolves `XrdSecProtObjectP`. Client protection first validates response lengths and vector sizes, skips no-protection responses, lazily loads the protection library under `protMutex`, and calls `New4Client`.

State and persistence: Process globals in `XrdSecProtection` cache `theProtector` and `protRC`. `protMutex` serializes lazy client loading. Loaded service/protector objects are process-resident; no disk state is written.

Dependencies and integration points: Uses `XrdOucPinLoader`, `XrdVersion`, `XProtocol` response structs, `XrdSecProtector`, `XrdSysError`, and `XrdSysMutex`. It is the bridge from public ABI symbols to actual shared libraries.

Risks: The protection `Load` has an early `return 1` before the later diagnostic/unload block, so some failure diagnostics are unreachable. Cached `protRC` makes a failed protection load sticky. Client-side errors go to `std::cerr` when no `XrdSysError` is available. ABI symbol names must match exactly.

Test signals: Missing library, bad symbol, version mismatch, service constructor failure, malformed short and oversized `kXR_protocol` responses, repeated concurrent `XrdSecGetProtection`, and successful lazy reuse of a loaded protector.
