# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/rdma/ib_user_mad.h

## Purpose

Defines the OFED user MAD ABI structures and ioctl command constants for registering agents, sending/receiving MAD packets, and enabling P_Key-index support.

## Main Definitions

- `IB_USER_MAD_ABI_VERSION` set to 5.
- ABI comment requiring identical struct layout on 32-bit and 64-bit architectures.
- `struct ib_user_mad_hdr`: packet metadata including agent ID, status, timeout, retries, MAD length, QPN, QKey, LID, SL, path bits, GRH presence, GID index, hop limit, traffic class, remote GID, flow label, P_Key index, and reserved bytes.
- `struct ib_user_mad`: header plus flexible `uint64_t data[]` payload.
- `struct ib_user_mad_reg_req`: agent registration request with returned ID, method mask, QPN, management class/version, OUI, and RMPP version.
- `IB_IOCTL_MAGIC` and ioctl constants:
  - `IB_USER_MAD_REGISTER_AGENT`
  - `IB_USER_MAD_UNREGISTER_AGENT`
  - `IB_USER_MAD_ENABLE_PKEY`

## Integration Notes

This is a user/kernel ABI header. It mirrors OFED definitions and is included by `ofed_kernel.h`.

## Risks and Gotchas

- Layout is explicitly ABI-sensitive across 32-bit userland and 64-bit kernels.
- Flexible payload is `uint64_t` aligned; command handlers must use the length field for bounds.
- P_Key index is only meaningful after enabling it on the user MAD file handle.
