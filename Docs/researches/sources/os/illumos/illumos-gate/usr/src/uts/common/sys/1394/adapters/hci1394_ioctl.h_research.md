# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/adapters/hci1394_ioctl.h

This header defines private/test ioctl command numbers and payload structs for direct `hci1394` hardware debugging.

Ioctl command set:
- OpenHCI register read/write.
- Vendor-specific OpenHCI register read/write.
- Bus reset.
- Self-ID interrupt count and current bus generation count.
- Self-ID buffer read.
- PHY register read/write.
- HBA/vendor information query.

Payload types include `hci1394_ioctl_wrreg_t`, `rdreg_t`, `wrvreg_t`, `rdvreg_t`, count structs, `read_selfid_t`, `wrphy_t`, `rdphy_t`, and `hbainfo_t`.

Risk notes:
- The file explicitly warns that writing OHCI, vendor, or PHY registers can destabilize hardware/software.
- `HCI11394_IOCTL` appears to contain an extra `1` in the macro name compared with the surrounding `HCI1394` naming, but it is consistently used as the command base in this file.
- `READ_SELFID` takes a user-supplied `uint32_t *buf` and count; implementation must validate/copy carefully.
