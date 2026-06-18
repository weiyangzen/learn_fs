# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/serial/silabs.c

## Role

Implements the Silicon Labs CP210x USB serial backend.

## Main Behavior

`slprobe` matches CP210x VID/PID pairs and installs `slops`.

The backend wraps vendor/interface USB control transfers with `slread`, `slwrite`, and `slput`. `slinit` records driver name `silabs`, reads the chip type, enables the port, reads current parameters, and retains the USB device reference.

`slgetparam` reads baud and line-control register fields, decoding data bits, parity, and stop bits. `slsetparam` writes the line-control register and baud value.

`slmodemctl` programs Silicon Labs flow-control registers for either CTS/RTS hardware flow control or direct DTR/RTS control. `slsendlines` updates DTR and RTS through `Setctrl`.

## Data Path

The backend uses generic endpoint discovery but overrides `wait4data` with a direct blocking read loop that temporarily drops the serial device lock and ignores zero-length reads.

## Integration Points

`slops` supplies initialization, parameter get/set, line control, modem control, custom data wait, and endpoint discovery.
