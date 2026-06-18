# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/nlm/sm_inter_xdr.c

Rpcgen-generated XDR serialization for the NSM structures declared in `sm_inter.h`. It serializes monitor names, callback identity, monitor ids, monitor requests, state-change notifications, state replies, enum results, combined result/state replies, and 16-byte private notification cookies.

The functions are straightforward wrappers around `xdr_string()`, `xdr_int()`, `xdr_enum()`, and `xdr_opaque()`, returning `FALSE` on decode/encode failure. The 16-byte `priv` field is important because `nlm_prot_impl.c` stores the NLM host sysid there to map NSM reboot notifications back to tracked hosts.
