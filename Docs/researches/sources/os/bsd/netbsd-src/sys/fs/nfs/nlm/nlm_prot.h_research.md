# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/nlm/nlm_prot.h

This rpcgen-generated header defines the NLM RPC protocol surface. It includes NLMv1/v3 and NLMv4 data structures, status enums, share-lock types, NSM notification structures, program/version/procedure numbers, client/server function prototypes, and XDR function prototypes.

Key contents:
- Defines `LM_MAXSTRLEN` and `MAXNAMELEN`.
- Defines NLM status enums `nlm_stats` and `nlm4_stats`, with v4 adding read-only filesystem, stale file handle, file-too-big, and failed statuses.
- Defines v1/v3 lock holder, test reply, stat, result, test result, lock, lock arguments, cancel arguments, test arguments, unlock arguments, share, share arguments, share result, and notify structures.
- Defines v4 equivalents with 64-bit offsets and lengths: `nlm4_holder`, `nlm4_lock`, `nlm4_testres`, `nlm4_lockargs`, `nlm4_cancargs`, `nlm4_unlockargs`, share structures, `nlm_sm_status`, and `nlm4_notify`.
- Defines NLM program `100021`, NSM pseudo-version/procedure, version 1, version 3, and version 4 procedure numbers.
- Declares client stubs and service handlers for synchronous procedures, asynchronous message procedures, asynchronous result procedures, share/unshare, non-monitored lock, free-all, and SM_NOTIFY.
- Declares `nlm_prog_*_freeresult()` helpers.
- Declares all XDR routines for NLM/NLMv4 structures and enums.

Important behavior:
- The file is generated and explicitly says not to edit it manually.
- NLMv1 uses 32-bit offsets and lengths, while NLMv4 uses 64-bit values; callers that bridge versions must validate range.
- Message procedures return `void` and deliver results later through result procedures; synchronous procedures return result structs directly.

Research notes:
- This header is the schema for `nlm_prot_clnt.c`, `nlm_prot_svc.c`, `nlm_prot_xdr.c`, and NLM implementation code.
- Protocol compatibility risks are struct layout changes, enum numeric changes, and accidental manual edits not reflected in the `.x` source.
