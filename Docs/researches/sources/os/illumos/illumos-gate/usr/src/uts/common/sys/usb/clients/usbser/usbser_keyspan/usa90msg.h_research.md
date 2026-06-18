# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbser/usbser_keyspan/usa90msg.h

Keyspan USA19HS/USA90-style async firmware message format definitions. It defines port control and status structures plus LCR, flow-control, RX/TX mode, RX error, port-state, and modem-status bits.

`keyspan_usa19hs_port_ctrl_msg` controls baud, LCR, RX/TX modes, TX/RX flow control, immediate XON/XOFF/char sends, RTS/DTR, forwarding thresholds/timeouts, ACK behavior, port enable, flush, break, loopback, RX forward, cancel RX XOFF, and status return.

`keyspan_usa19hs_port_status_msg` reports MSR, CTS/DCD/DSR/RI, XOFF state, break, accumulated overrun/parity/frame errors, port state, message/char acknowledgements, and control response.
