# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/sol_ucma/sol_rdma_user_cm.h

This Solaris UCMA compatibility header aliases OFED `rdma_user_cm.h` ABI structures into Solaris-specific names and defines 32/64-bit variants for structures whose native layout differs.

Core definitions:
- Typedefs map all RDMA UCM command and response structs to `sol_ucma_*` names.
- Packed 32-bit and 64-bit versions are provided for bind-address and join-multicast commands.
- The 64-bit variants add reserved padding where needed to preserve expected alignment and structure size.

Risk-sensitive invariants:
- This file is part of user/kernel ABI adaptation for sol_ucma.
- The compat variants are necessary because `rdma_user_cm.h` carries user response pointers and socket-address payloads.
- Any change must preserve the packed wire/control ABI used by user-space RDMA CM libraries.
