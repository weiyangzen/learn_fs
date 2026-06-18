# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba.h

Top-level USBA client-driver include wrapper. It pulls in common kernel/DDI headers needed by USB client drivers and then includes `<sys/usb/usbai.h>`.

The file defines no driver state, constants, or functions of its own beyond include guards and C++ linkage wrapping. Its role is dependency aggregation for USB client-driver interfaces.

Because it is broad and public-facing, changes here have large compile-time and API-surface impact across USB drivers. It should remain minimal and stable.
