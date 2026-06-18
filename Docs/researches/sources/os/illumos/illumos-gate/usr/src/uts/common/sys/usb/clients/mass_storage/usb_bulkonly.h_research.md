# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/mass_storage/usb_bulkonly.h

USB Mass Storage Bulk-Only Transport definitions. It provides class request constants for reset and GET_MAX_LUN, CBW signature/direction/CDB length constants, byte extraction macros for CBW fields, and CSW layout/status constants.

The only structure is `usb_bulk_csw_t`, a byte-wise representation of the 13-byte Command Status Wrapper, including signature, tag, residue, and status fields.

It also defines `IOMEGA_CMD_CARTRIDGE_PROTECT` as a vendor-specific command needed for certain bulk-only devices.
