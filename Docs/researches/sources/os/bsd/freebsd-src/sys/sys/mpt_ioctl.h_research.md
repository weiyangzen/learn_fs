# File Research: sources/os/bsd/freebsd-src/sys/sys/mpt_ioctl.h

Defines ioctl ABI for LSI MPT-Fusion host adapter configuration and RAID actions.

Key content:
- Includes MPI type/config headers from `dev/mpt/mpilib`.
- `struct mpt_cfg_page_req` carries a config page header, page address, buffer pointer, length, and IOC status.
- `struct mpt_ext_cfg_page_req` is the extended-page variant.
- `struct mpt_raid_action` carries RAID action, volume bus/id, physical disk number, action data word, buffer, length, volume status, action data array, action status, IOC status, and write flag.
- Ioctls:
  - `MPTIO_READ_CFG_HEADER`
  - `MPTIO_READ_CFG_PAGE`
  - `MPTIO_READ_EXT_CFG_HEADER`
  - `MPTIO_READ_EXT_CFG_PAGE`
  - `MPTIO_WRITE_CFG_PAGE`
  - `MPTIO_RAID_ACTION`
- On amd64, 32-bit compatibility structs/ioctls replace pointers with uint32_t buffer fields.

Research relevance:
- Storage-controller management ABI for configuration pages and RAID actions.
- Relevant to block-storage research where device ioctls expose hardware configuration and status.

Cautions:
- Callers must include correct page type/extended type, page number, version, and page address.
- 32-bit compatibility ABI is explicitly separate on amd64.
