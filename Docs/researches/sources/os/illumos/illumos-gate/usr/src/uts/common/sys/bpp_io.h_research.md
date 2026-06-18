# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/bpp_io.h

`bpp_io.h` defines the ioctl ABI for the bidirectional parallel port driver for the Zebra SBus card. It includes ioctl commands for getting/setting transfer parameters, output pins, error status, and test I/O.

The file defines handshake modes, maximum timeout, `bpp_transfer_parms` timing/handshake configuration, `bpp_pins` input/output pin masks, and `bpp_error_status` for timeout, bus error, and pin error state.
