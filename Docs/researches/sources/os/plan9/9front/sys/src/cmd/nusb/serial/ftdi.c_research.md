# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/serial/ftdi.c

## Role

Implements the FTDI USB serial backend for `nusb/serial`. It probes a large VID/PID table, identifies FTDI chip families, configures FTDI-specific USB control requests, and adapts FTDI packet framing to the generic `Serialops` interface.

## Main Behavior

The file defines extensive FTDI and FTDI-compatible product IDs, command constants, chip type constants, flow-control flags, status bits, packet header bits, and bit-bang/JTAG settings.

`ftprobe` matches the device with `ftinfo`, then calls `ftgettype` to infer chip type from device release number, number of interfaces, USB speed packet size, and product string. Multi-interface parts are treated as FT2232/FT4232 class devices, and devices whose product string contains `jtag` expose interface 0 as JTAG.

`ftsetparam` programs line data format, flow control, and baud divisor. Baud divisor calculation is split between SIO fixed baud codes, FT8U232AM-style divisors, and FT232BM/newer fractional divisors. Special 38400-baud custom divisor handling exists for Tira and USB-UIRT devices.

FTDI incoming data has a two-byte status header per USB packet. `cpdata` strips these headers and feeds modem/error status into the `Serialport`. For old SIO-style output headers, `ftsetouthdr` prepends the port/length byte.

## Concurrency And Data Path

`ftinit` resets the port, optionally configures JTAG latency/MPSSE bit mode, and starts `statusreader`. `statusreader` creates a buffered channel and starts `epreader`, which reads the bulk-in endpoint, strips FTDI headers, recovers from transient read failures, and pushes packets to waiters.

`wait4data` synchronizes with the reader using `w4data`/`gotdata` channels and serves buffered bytes to generic serial reads. `wait4write` writes through the bulk-out endpoint with any required FTDI output header.

## Integration Points

The exported `ftops` table supplies:

- initialization and endpoint max-packet setup
- generic endpoint discovery
- parameter setting
- pipe purge/reset
- modem line control
- flow control
- break control
- custom read/write wait handlers

## Notable Details

The implementation uses `ser->maxrtrans`, `ser->maxwtrans`, `ser->inhdrsz`, `ser->outhdrsz`, and `ser->baudbase` to communicate FTDI framing and timing constraints back to `serial.c`.

The JTAG path reuses the serial device framework but marks the port as `isjtag`, suppressing normal serial control handling in the generic layer.
