# sources/user-network-fs/nfs-ganesha/src/Protocols/RQUOTA/rquota_setactivequota.c

Purpose: placeholder implementation for RQUOTA SETACTIVEQUOTA.

Important APIs/types/functions: exports `rquota_setactivequota` and `rquota_setactivequota_Free`.

Control flow: logs the operation and returns success without changing quota activation.

State and persistence: no state is modified.

Dependencies and integration points: compiled into the RQUOTA object target and satisfies dispatch symbol requirements.

Risks and test signals: the success return may mask unimplemented semantics for clients that expect active quota changes. Test client behavior and consider explicit unsupported status if protocol compatibility allows it.
