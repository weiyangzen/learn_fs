# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/oce/oce_ioctl.h

This small header defines private OCE ioctl command values and the driver-query payload.

Key contents:
- OCE ioctl base value `OCE_IOC`.
- Private ioctl commands:
  - `OCE_ISSUE_MBOX`
  - `OCE_QUERY_DRIVER_DATA`
- Supported query version `OCN_VERSION_SUPPORTED`.
- `MAX_SMAC` limit for secondary MAC addresses.
- `struct oce_driver_query`, carrying version, secondary MAC address table, primary MAC address, driver name/version strings, and secondary-MAC count.

Dependencies:
- Uses `ETHERADDRL` but does not include the defining Ethernet header itself, relying on including context.

Research notes:
- `OCE_ISSUE_MBOX` exposes a mailbox-issue path, so callers and implementation must validate payload size and firmware-visible structures carefully.
- `OCE_QUERY_DRIVER_DATA` is a small management/introspection ABI for driver identity and MAC addresses.
