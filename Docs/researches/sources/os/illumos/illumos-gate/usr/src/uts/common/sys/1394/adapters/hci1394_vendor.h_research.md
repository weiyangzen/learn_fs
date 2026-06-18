# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/adapters/hci1394_vendor.h

This private header defines vendor-specific adapter support for `hci1394`.

Key constants:
- Sun vendor ID `0x108E`.
- Sun RIO 1394 device ID `0x1102`.
- Up to `VENDOR_MAX_REGSETS` (`6`) vendor register mappings.

Main types:
- `hci1394_vendor_handle_t`: opaque vendor module handle.
- `hci1394_vendor_info_t`: PCI vendor/device/revision, OHCI version/vendor ID, and vendor register count.
- `hci1394_vendor_reg_t`: one mapped vendor register region address and DDI access handle.
- `hci1394_vendor_t`: OHCI handle, register count/array, driver info, and cached vendor info.

APIs:
- Init/fini/resume.
- Vendor register read/write by register set and offset.

Research note:
- The include guard uses `_HCI1394_VERSION_H` even though the file is `hci1394_vendor.h`; it is internally consistent but semantically misnamed.
