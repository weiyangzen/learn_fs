# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/serial/serial.h

## Role

Defines shared data structures, constants, and helper prototypes for the `nusb/serial` framework and its chip backends.

## Main Structures

`Serialops` is the backend operation table. It includes hooks for endpoint setup/discovery, initialization, get/set parameters, pipe clearing, reset, line control, modem control, break control, status reads, and custom read/write waiting.

`Serialport` stores per-port state: endpoint devices, control-line state, baud/format settings, modem state, error counters, interface number, read buffering, and 9P request queues.

`Serial` stores per-device state: USB device, backend driver name/type, recovery counter, operation table, number of interfaces, JTAG interface index, transfer sizes, FTDI-style header sizes, and baud base.

`Cinfo` is a simple VID/PID match entry with an optional backend-assigned ID.

## Constants And Prototypes

Defines shared buffer/interface limits, software flow control bytes, DTR/RTS bits, `serialdebug`, debug print macro, and helpers such as `serialrecover`, `serialreset`, `findendpoints`, `openeps`, `serdumpst`, and `matchid`.
