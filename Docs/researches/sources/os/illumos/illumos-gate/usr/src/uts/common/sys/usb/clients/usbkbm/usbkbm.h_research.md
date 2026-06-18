# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbkbm/usbkbm.h

USB keyboard module state and translation constants. It defines LED masks, modifier masks/keycodes, rollover constant, boot keyboard report size, open/qwait flags, polled key state, max packet size, and report format metadata.

`usbkbm_state_t` owns kbtrans state, STREAMS queues, report format, HID parser handle, layout, LED ioctl sequencing, previous/pending USB packets, HID polled callback, pending ioctl/link messages, bufcall ID, console polled I/O state, virtual keyboard type, vid/pid, polled scancode ring, and boot/report protocol selection.

The file also defines Sun Japanese keyboard layout/vendor/product constants, USB keymap sizing, saved global keyboard state, debug masks, and index conversion constants for PC/USB key tables.
