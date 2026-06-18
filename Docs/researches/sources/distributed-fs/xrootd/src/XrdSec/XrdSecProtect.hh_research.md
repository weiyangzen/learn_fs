# sources/distributed-fs/xrootd/src/XrdSec/XrdSecProtect.hh

Purpose: Declares the per-connection request protection object and the `NEED2SECURE` fast path macro.

Important APIs and types: `XrdSecProtect` exposes `Delete`, member-function pointer `Need2Secure`, `Secure`, and `Verify`. Protected constructors distinguish client initialization from server cloning. `SetProtection` is used by `XrdSecProtector` to configure levels and vectors.

Control flow: Callers check `NEED2SECURE(protP)(ClientRequest&)`, then call `Secure` before sending or `Verify` when receiving the companion `kXR_sigver` request.

State and persistence: Holds non-owning `XrdSecProtocol *authProt`, active vector pointers, local vector storage, request settings, sequence counters, and option flags. State is in-memory and tied to a connection.

Dependencies and integration points: Includes `XProtocol.hh`, forward declares `XrdSecProtocol`, and friends `XrdSecProtector` for controlled construction/configuration.

Risks: `Need2Secure` is public and must be invoked through the macro to avoid null-pointer misuse. The auth protocol lifetime must exceed the protection object. `Secure` returns malloc-backed request storage that callers must free.

Test signals: Compile macro call sites, verify no signing when `protP` is null, confirm `Delete` cleanup, and test ownership of returned `SecurityRequest` buffers.
