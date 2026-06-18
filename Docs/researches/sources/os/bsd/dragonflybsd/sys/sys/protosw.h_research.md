# File Research: sources/os/bsd/dragonflybsd/sys/sys/protosw.h

Network protocol switch and protocol user-request interface definitions.

Key responsibilities:
- Defines `struct pr_output_info`.
- Defines kernel `netmsg_t` and `struct protosw`, containing protocol type/domain/number/flags, port selection, input/output/control hooks, initialization/drain hooks, and user-request table.
- Defines protocol timer constants and protocol flags for atomic/addressed messages, connection requirement, rights passing, implied open/close, MPSAFE state, sync port, and async send/receive/connect behavior.
- Defines `PRU_*` user-request operation numbers and optional debug name arrays.
- Defines `struct pru_attach_info` and `struct pr_usrreqs`, including netmsg-based protocol operations and synchronous send/receive/preconnect/preattach callbacks.
- Declares not-supported helpers, CPU0 port helpers, protocol-control command constants, ctloutput constants, and protocol lookup/control APIs.
- Defines `PR_GET_MPLOCK` and `PR_REL_MPLOCK` wrappers for non-MPSAFE protocols.

Important behavior:
- DragonFly routes many protocol operations through LWKT message ports and protocol threads.
- Some operations remain synchronous in user context, notably generic send/receive paths and preconnect/preattach.
- Non-MPSAFE protocol calls are wrapped in the MP lock.
- `pr_ctlport` and Toeplitz/netisr selection control protocol-thread placement.

Dependencies:
- Includes `sys/types.h`.
- Kernel structures depend on sockets, mbufs, sockopts, sockbufs, ucred, uio, ifnet, stat, rlimit, vnodes, LWKT ports, and netmsg definitions.

Notable risks:
- Protocol callback contracts mix synchronous and asynchronous paths; ownership of mbufs/control data must follow the specific hook.
- `PRU_NREQ`, debug request arrays, and enum values must remain synchronized.
- MP-lock wrappers require correct `PR_MPSAFE` flagging.
