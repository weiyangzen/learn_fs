# sources/user-network-fs/nfs-ganesha/src/Protocols/NLM/sm_notify.c

Purpose: standalone helper program to send an NSM `SM_NOTIFY` RPC, useful for notification delivery/testing outside the main daemon.

Important APIs/types/functions: defines `LogMallocFailure`, `nsm_notify_1`, and `main`. It parses `-p`, `-l`, `-m`, `-r`, and `-s` options and uses TI-RPC datagram client calls.

Control flow: `main` validates required options, creates and binds a nonblocking UDP socket to the local address/port, resolves the remote statd port with `rpcb_find_mapped_addr`, creates a datagram RPC client, fills `notify` with monitor name and state, calls `nsm_notify_1`, frees rpcbind buffers, destroys the client, closes the socket, and exits. `nsm_notify_1` sends `SM_NOTIFY` with a 15-second timeout.

State and persistence: no daemon state. It sends one remote notification and exits.

Dependencies and integration points: depends on generated NSM XDR, TI-RPC, rpcbind, socket APIs, and Ganesha memory wrappers.

Risks and test signals: option length checks are bounded, but `inet_addr` accepts limited forms and error reporting is coarse. Test missing options, bind failure, rpcbind failure, successful notify, non-default port, and unreachable remote statd.
