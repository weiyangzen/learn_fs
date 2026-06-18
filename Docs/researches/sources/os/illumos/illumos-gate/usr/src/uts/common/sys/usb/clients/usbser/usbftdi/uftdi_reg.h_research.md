# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbser/usbftdi/uftdi_reg.h

FTDI USB serial protocol/register constants, derived from NetBSD/FreeBSD lineage and FTDI protocol documentation. It defines vendor request numbers, port identifiers, FTDI chip types, reset commands, baud divisor values for SIO and 8U232AM-style chips, data format bitfields, modem-control commands, flow-control values, and status decoding.

The comments document each vendor request format in detail: reset, set baud rate, set data, modem control, flow control, event char, error char, modem status, and endpoint data framing.

Status macros decode FTDI IN endpoint leading modem/line status bytes and OUT endpoint tag construction. Line-status bits mirror 16550-style overrun, parity, framing, break, THRE, and TEMT semantics.
