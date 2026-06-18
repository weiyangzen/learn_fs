# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/rdma/rdma_user_cm.h

This OFED-derived packed ABI header defines the user/kernel command protocol for the RDMA user CM device.

Core definitions:
- ABI version `RDMA_USER_CM_ABI_VERSION` is `4`; private connection data is capped at `RDMA_MAX_PRIVATE_DATA` bytes.
- Command numbers cover create/destroy ID, bind/resolve/query route, connect/listen/accept/reject/disconnect, init QP attr, get/set option, notify, multicast join/leave, and event retrieval.
- Packed request/response structs encode user handles, response addresses, IDs, socket addresses, timeouts, route records, connection parameters, UD parameters, event responses, and options.

Risk-sensitive invariants:
- `#pragma pack(1)` makes this a strict binary ABI; padding/reserved fields are deliberate.
- Many structures carry user pointers or response addresses, so compat conversion and copyin/copyout code must preserve 32/64-bit layout.
- Route query response supports two IB paths and embeds IPv6-sized source/destination socket addresses.
