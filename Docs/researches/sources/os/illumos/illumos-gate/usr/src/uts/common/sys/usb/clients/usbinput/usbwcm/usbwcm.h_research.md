# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbinput/usbwcm/usbwcm.h

USB Wacom tablet event ABI and kernel driver definitions. The file includes Sun, FreeBSD, and NetBSD-derived licensing/copyright material.

The user-visible portion defines event ioctl commands, `event_dev_id`, `event_abs_axis`, and `event_input`, plus event type/code spaces for sync, buttons, relative axes, absolute axes, and miscellaneous serial data.

The `_KERNEL` portion defines Wacom vendor/product IDs, tool IDs, pad serial constants, ioctl command numbers, protocol/model structs, protocol table, softc state, USBWCM STREAMS state, transparent ioctl copyin state, supported Wacom device table with dimensions/pressure ranges, packet extraction macros, bitmap helpers, bitmap sizes, and debug mask.

It embeds a static `uwacom_devs[]` device table covering Graphire, Bamboo, Cintiq, Volito, PenPartner, Intuos3, and Intuos4 variants.
