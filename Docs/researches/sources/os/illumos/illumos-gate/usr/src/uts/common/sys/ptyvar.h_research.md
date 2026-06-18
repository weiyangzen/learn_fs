# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ptyvar.h

## Role

`ptyvar.h` defines legacy pseudo-terminal driver state, packet/user-control ioctl constants, M_CTL message types, and kernel globals for Berkeley-style pty naming.

## Data Model

`struct pty` contains:
- pty flags.
- queued ioctl message blocks and queued-byte count.
- `tty_common_t` state.
- bufcall ID.
- selecting processes for read/write/exception.
- subsidiary device/vnode references.
- controller-side process group.
- pending controller message/control bytes.
- per-pty mutex and condition variables for flags/read/write state.

Flags cover polling collision, nonblocking/async I/O, open/carrier state, subsidiary gone, packet mode, stop/start state, remote mode, no-stop flow control, user-control modes, ioctl-in-progress, close wait, read/write serialization, and waiters.

## Protocol Constants

The M_CTL message constants describe canonicalization and terminal flag behavior between STREAMS modules. The pty ioctl set includes packet mode (`TIOCPKT`), user-control modes, input queue size/space queries, and legacy Sun `ttysize` get/set calls.

## Kernel Declarations

Under `_KERNEL`, the header declares `npty`, `pty_softc`, `ptcph`, and `pty_initspace()`, plus the Berkeley pty bank/digit naming strings.

## Research Notes

This is a legacy pty driver header, distinct from `ptms.h`. It combines STREAMS tty state with BSD-compatible packet mode and naming conventions.
