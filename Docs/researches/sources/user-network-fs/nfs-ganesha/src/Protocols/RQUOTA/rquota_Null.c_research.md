# sources/user-network-fs/nfs-ganesha/src/Protocols/RQUOTA/rquota_Null.c

Purpose: implements the RQUOTA NULL procedure for basic RPC reachability.

Important APIs/types/functions: exports `rquota_Null` and `rquota_Null_Free`.

Control flow: logs `RQUOTA_NULL` at full debug and returns success. Result cleanup is intentionally empty.

State and persistence: no state is touched.

Dependencies and integration points: includes RQUOTA and common NFS core/export headers to conform to protocol dispatch signatures.

Risks and test signals: low risk. Test a NULL RPC and result cleanup behavior.
