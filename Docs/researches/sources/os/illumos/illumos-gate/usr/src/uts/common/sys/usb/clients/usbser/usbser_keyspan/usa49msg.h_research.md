# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbser/usbser_keyspan/usa49msg.h

Keyspan USA49W async firmware message format definitions. It defines port control/status messages plus global control/status/debug messages and RX data status bit meanings.

`keyspan_usa49_port_ctrl_msg` is a detailed host-to-device command structure covering baud clocking, LCR, flow control, RTS/DTR, forwarding behavior, ACK thresholds, loopback, TX/RX on/off/flush/break/forward, status return, data-toggle reset, port enable, and port disable.

`keyspan_usa49_port_status_msg` reports CTS/DCD/DSR/RI, TX-off and XOFF state, RX enable state, control response, TX ACK, and RS-232 validity.

The comments define raw USB IN/OUT data message framing, including status-byte interleaving for parity/framing/break reporting and overrun interpretation.
