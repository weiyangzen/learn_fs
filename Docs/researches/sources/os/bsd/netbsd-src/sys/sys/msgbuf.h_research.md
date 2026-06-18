# File Research: sources/os/bsd/netbsd-src/sys/sys/msgbuf.h

## Purpose
Defines the kernel circular message buffer used for console/log storage.

## Main API
- `struct kern_msgbuf` with magic, write/read offsets, size, and flexible buffer.
- Magic constant: `MSG_MAGIC`.
- Kernel globals: `msgbufmapped`, `msgbufenabled`, `msgbufp`, `log_open`.
- Kernel functions: `initmsgbuf`, `loginit`, `logputchar`.
- Inline helper: `logenabled`.

## Dependencies
Minimal; kernel users rely on the broader kernel environment for globals and initialization.

## Risks and Notes
`logenabled` checks both global enable state and the buffer magic. The buffer uses `char msg_bufc[1]`, an old flexible-array pattern, so allocation must account for the actual backing size.
