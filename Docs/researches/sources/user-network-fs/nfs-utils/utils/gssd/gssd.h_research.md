<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/gssd.h -->
# sources/user-network-fs/nfs-utils/utils/gssd/gssd.h

## Purpose
This header defines the shared daemon configuration, rpc_pipefs client structures, upcall request structures, and public upcall-handling APIs for `rpc.gssd`.

## APIs And Types
It defines default paths and names, upcall timeout bounds, `RPC_CHAN_BUF_SIZE`, auth type constants, and many extern configuration variables. `struct clnt_info` tracks one kernel client directory, its parsed server/service/protocol data, pipe fds/events, watch descriptor, sockaddr, and fallback upcall fields. `struct clnt_upcall_info` packages one worker request. `struct upcall_thread_info` tracks watchdog metadata, deadline, uid, fd, and cancellation flags. Public functions include `handle_krb5_upcall`, `handle_gssd_upcall`, `free_upcall_info`, `gssd_free_client`, and `do_error_downcall`.

## State, Dependencies, And Integration
The header depends on GSSAPI, libevent, pthreads, sys/queue, and nfs-utils state directory macros. It connects `gssd.c`, `gssd_proc.c`, and `krb5_util.c` through shared globals.

## Risks And Test Signals
Risks include many mutable extern globals, reference-counted client lifetimes, legacy and modern pipe paths coexisting, and structs carrying both parsed and fallback service info. Test compile users under strict warnings and runtime paths for legacy `krb5` pipe, modern `gssd` pipe, cancellation flags, and config defaults.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/gssd.h -->
