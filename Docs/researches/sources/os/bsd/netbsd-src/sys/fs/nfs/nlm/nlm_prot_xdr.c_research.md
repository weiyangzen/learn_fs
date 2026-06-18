# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/nlm/nlm_prot_xdr.c

Rpcgen-generated XDR serialization for NLM protocol data structures. It covers legacy NLM and NLMv4 statuses, holders, locks, lock/test/cancel/unlock arguments, share arguments/results, notify records, NSM status callbacks as used by NLM, and test/result unions.

Legacy NLM uses 32-bit offsets/lengths and `LM_MAXSTRLEN` caller names; NLMv4 uses 64-bit offsets/lengths, uint32 pids, and `MAXNAMELEN` caller names. Union encoders only serialize lock-holder details for denied test replies.

Every function returns `FALSE` on the first failed XDR primitive. The file is not policy-bearing; correctness depends on matching `nlm_prot.h` structure layout and the RPC dispatch tables in `nlm_prot_svc.c`.
