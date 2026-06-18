# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hubd/hubd_impl.h

Hub driver ioctl/devctl implementation header for USB cfgadm integration. It defines `DEVCTL_AP_CONTROL` subcommands for retrieving cfgadm name, current configuration, device path, and refreshing the USB device database, plus string descriptor sub-options.

It defines native and 32-bit-compatible `hubd_ioctl_data` layouts with command, port, get-size flag, user buffer pointer, buffer size, and reserved argument.

The file is an ioctl ABI bridge between userland cfgadm tooling and hubd internals. Its main compatibility concern is preserving structure layout and correct 32-bit pointer handling on 64-bit kernels.
