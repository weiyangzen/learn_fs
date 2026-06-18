# File Research: sources/os/bsd/openbsd-src/sys/sys/protosw.h

Defines the network protocol switch table and socket user-request dispatch interface.

Key contents:
- `struct pr_usrreqs`: socket operation callbacks for attach, detach, bind, listen, connect, accept, disconnect, shutdown, receive notification, send, abort, control, sense, out-of-band, sockaddr/peeraddr, flowid, and connect2.
- `struct protosw`: socket type/domain/protocol/flags, protocol input/control hooks, user request table, init/timer/sysctl hooks.
- Protocol timer rates `PR_SLOWHZ` and `PR_FASTHZ`.
- Protocol flags such as atomic/addressed messages, connection requirement, receive callbacks, rights passing, splicing, MP input, and MP-safe sysctl.
- Legacy `PRU_*`, `PRC_*`, and `PRCO_*` command constants plus optional debug name arrays.

Kernel APIs:
- Protocol lookup: `pffindproto`, `pffindtype`, `pffinddomain`, `pfctlinput`.
- Inline wrappers `pru_*` dispatch through `so->so_proto->pr_usrreqs`, returning `EOPNOTSUPP` for optional unsupported operations.

Risk notes:
- Some inline wrappers free mbufs on unsupported operations while others leave ownership to caller/protocol; ownership expectations must be followed exactly.
