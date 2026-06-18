# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/serial/serial.c

## Role

Provides the generic `nusb/serial` 9P server and hardware-independent USB serial framework. Chip-specific backends plug in through `Serialops`.

## Main Behavior

`threadmain` opens the USB device, allocates `Serial`, probes supported backends in order (`ucons`, `ftdi`, `silabs`, `prolific`, `ch340`, `acm`), opens endpoints for each serial interface, initializes ports, names them `eiaU...` or `jtag...`, creates read/write request queues, and posts a share service named `<devid>.serial`.

The exposed file tree contains two files per port: a data file and a `ctl` file. Reads and writes on data files are queued and processed by `procread` and `procwrite`; `ctl` reads dump serial state and `ctl` writes parse Plan 9 serial control commands.

## Control Path

`serialctl` parses compact commands for baud, data bits, parity, stop bits, RTS/DTR, modem flow control, breaks, flushing, wait timer, and XON/XOFF writes. It drains output before parameter changes when needed, delegates hardware-specific operations through `Serialops`, and resets recovery state on success.

`serdumpst` formats current settings and error counters.

## Endpoint Handling

`findendpoints` finds bulk in/out endpoints and an optional interrupt endpoint. `openeps` opens endpoint devices, sets timeout/debug controls, applies backend endpoint tuning, and opens data file descriptors in read/write mode.

## Error Handling

`serialrecover` handles detached devices, endpoint unstalling, fatal channel closure, whole-device reset, and backend reset escalation based on the recovery counter. `serialreset` drains all ports and calls the backend reset hook.

## Integration Points

The server depends on backend-provided hooks for initialization, parameter handling, pipe recovery, line control, breaks, endpoint discovery, and optional custom read/write paths.
