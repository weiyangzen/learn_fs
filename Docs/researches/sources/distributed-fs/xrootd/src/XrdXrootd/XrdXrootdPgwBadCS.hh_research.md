# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdPgwBadCS.hh

Purpose: declares a compact helper for tracking bad checksum offsets during one pgwrite request.

Important APIs/types/functions: `boAdd`, `boInfo`, `boReset`, constructor with path ID, internal `ServerResponseBody_pgWrCSE`, fixed `badOffs[kXR_pgMaxEpr]`, `boCount`, and `pathID`.

Control flow: users reset at request setup, call `boAdd()` for each failed page/segment, then call `boInfo()` once when building the final response.

State and persistence behavior: per-object in-memory request state only; file-level state is updated indirectly by `boAdd()`.

Dependencies: `XProtocol/XProtocol.hh` and forward-declared `XrdXrootdFile`.

Integration points: base class for `XrdXrootdPgwCtl` and optional collaborator for `XrdXrootdPgrwAio`.

Risks: fixed offset capacity requires protocol and implementation limits to stay aligned. `boReset()` clears only the count, leaving old bytes in arrays but making them ignored.

Test signals: reset reuse, offset capacity boundaries, response length calculation, and path ID propagation into traces.
