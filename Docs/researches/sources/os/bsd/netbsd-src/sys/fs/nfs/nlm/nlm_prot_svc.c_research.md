# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/nlm/nlm_prot_svc.c

Generated-style RPC dispatcher for the NLM program. It decodes incoming RPC procedure numbers for versions 0, 1, 3, and 4, selects the correct XDR argument/result routines, invokes the local `*_svc` implementation function, sends replies when requested, frees decoded arguments, frees result storage, and releases the service request.

`nlm_prog_0()` only dispatches `NLM_SM_NOTIFY`. `nlm_prog_1()` handles classic NLM test, lock, cancel, unlock, granted, async message, and async result procedures. `nlm_prog_3()` delegates common version 1 procedures to `nlm_prog_1()` and adds share, unshare, non-monitored lock, and free-all. `nlm_prog_4()` dispatches the corresponding NLMv4 procedure set.

The file is tightly coupled to `nlm_prot_server.c` for service functions and `nlm_prot_xdr.c` for XDR codecs. It follows rpcgen conventions, including union argument/result storage and returning no normal RPC reply for asynchronous message handlers whose service function returns false.
