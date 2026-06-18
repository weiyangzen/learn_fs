# sources/distributed-fs/xrootd/src/XrdSec/XrdSecProtector.hh

Purpose: Declares the protection policy parameters and factory interface that manages `XrdSecProtect` objects.

Important APIs and types: `XrdSecProtectParms` defines levels `secNone` through `secPedantic` and options `doData`, `relax`, and `force`. `XrdSecProtector` exposes `Config`, `LName`, `New4Client`, `New4Server`, and `ProtResp`, plus `lrType` for local/remote slots.

Control flow: Server code configures the protector once, sends `ProtResp` in protocol negotiation, and creates server-side protectors after authentication. Client code creates a protector from the negotiated response.

State and persistence: The abstract class declares no fields. The default implementation stores global configured templates and flags.

Dependencies and integration points: Uses `XPtypes.hh`, protocol response structs, `XrdNetAddrInfo`, `XrdSecProtocol`, and `XrdSysLogger`. The exported singleton is resolved by the loader as `XrdSecProtObjectP`.

Risks: `force` explicitly allows operation without encrypted hashes, which should be treated as a compatibility/testing downgrade. `relax` permits unsigned old clients. The ABI is virtual and plug-in-facing.

Test signals: Validate enum-to-wire mappings, options-to-response flags, client and server object construction, and plug-in replacement compatibility.
