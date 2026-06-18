# sources/user-network-fs/nfs-ganesha/src/Protocols/RQUOTA/rquota_getactivequota.c

Purpose: placeholder implementation for RQUOTA GETACTIVEQUOTA.

Important APIs/types/functions: exports `rquota_getactivequota` and `rquota_getactivequota_Free`.

Control flow: logs the operation and returns success without filling a meaningful quota result.

State and persistence: no state is read or written.

Dependencies and integration points: compiled into the RQUOTA target and used by dispatch tables, but currently does not call FSAL quota APIs.

Risks and test signals: clients expecting active quota semantics may see an effectively unimplemented result path. Test protocol compatibility and confirm generated XDR defaults are acceptable for supported clients.
