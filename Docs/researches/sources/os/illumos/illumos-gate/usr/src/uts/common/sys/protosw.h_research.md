# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/protosw.h

## Purpose
Defines the classic protocol switch table interface for socket protocol modules, protocol flags, user-request command codes, control-input command codes, and control-output request codes.

## Main Interfaces
- `struct protosw`: socket type, domain, protocol number, flags, protocol hooks, user request hook, init/fast/slow timeout/drain hooks.
- Timer rates:
  - `PR_SLOWHZ`
  - `PR_FASTHZ`
- Protocol flags:
  - `PR_ATOMIC`
  - `PR_ADDR`
  - `PR_CONNREQUIRED`
  - `PR_WANTRCVD`
  - `PR_RIGHTS`
  - `PR_OOB_ADDR`
- User request codes:
  - `PRU_ATTACH`, `PRU_DETACH`, `PRU_BIND`, `PRU_LISTEN`, `PRU_CONNECT`, `PRU_ACCEPT`
  - disconnect/shutdown/send/receive/OOB/control/address/timer/protocol internal requests.
- Optional debug name arrays under:
  - `PRUREQUESTS`
  - `PRCREQUESTS`
  - `PRCOREQUESTS`
- Control-input commands:
  - `PRC_IFDOWN`, `PRC_ROUTEDEAD`, unreachable/redirect/time-exceeded/parameter/gateway commands.
- Control-output commands:
  - `PRCO_GETOPT`
  - `PRCO_SETOPT`
- Kernel lookup:
  - `pffindproto()`
  - `pffindtype()`

## Dependencies And Relationships
Part of the socket/protocol stack ABI inherited from BSD/AT&T lineage. References `struct domain`, sockets, mbufs, and protocol-specific control paths by convention.

## Research Notes
The comments warn that some control-input numeric values are assumed by existing code and should be changed only with extreme care.
