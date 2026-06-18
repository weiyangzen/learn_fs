# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/mi-mctp-compat.h

Compatibility definitions for systems whose installed headers lack Linux MCTP socket definitions.

Contents:
- Defines `mctp_eid_t`.
- Defines `struct mctp_addr`.
- Defines `struct sockaddr_mctp`.
- Defines MCTP constants:
  - `MCTP_NET_ANY`
  - `MCTP_ADDR_NULL`
  - `MCTP_ADDR_ANY`
  - `MCTP_TAG_MASK`
  - `MCTP_TAG_OWNER`

Research notes:
- This is only used when `NVME_HAVE_LINUX_MCTP_H` is false.
- It keeps MCTP support buildable on systems where `linux/mctp.h` has not propagated into standard include paths.
