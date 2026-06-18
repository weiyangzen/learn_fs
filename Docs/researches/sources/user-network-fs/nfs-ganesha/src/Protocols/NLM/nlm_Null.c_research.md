# sources/user-network-fs/nfs-ganesha/src/Protocols/NLM/nlm_Null.c

Purpose: implements the NLM NULL procedure, a no-op endpoint for RPC reachability.

Important APIs/types/functions: exports `nlm_Null` and `nlm_Null_Free`.

Control flow: logs the call on `COMPONENT_NLM` and returns success. The result free function has no work.

State and persistence: no runtime state is read or mutated.

Dependencies and integration points: depends only on NLM/common headers and the standard NFS procedure signature.

Risks and test signals: minimal logic risk. Test that the procedure dispatches across supported NLM versions and does not require initialized result storage.
