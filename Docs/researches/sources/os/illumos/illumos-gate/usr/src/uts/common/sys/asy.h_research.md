# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/asy.h

## Purpose

`asy.h` defines hardware registers, bit fields, ring-buffer macros, flags, and state structures for the asynchronous serial UART driver.

## Hardware Definitions

The file defines bus type names, COM port I/O addresses, UART hardware type constants from 8250/16550 through 16950, and an `asy_reg_t` enum covering base UART registers plus 16750/16650/16950 extended and indexed registers.

It defines bit masks for interrupt enable, FIFO control and trigger levels, interrupt status, line control, modem control/status, line status, scratch-pad testing, 16650 enhanced feature access, and 16950 additional control/status/clock registers.

## Driver State

Ring macros manage a 64 Ki-entry receive ring with embedded error bits. `struct asycom` stores per-port hardware/common state, locks, interrupt handles, soft interrupt state, saved registers, console polling state, access handle, and 16950 settings.

`struct asyncline` stores STREAMS/TTY line state, output block, condition variables, flags, flow-control state, receive ring pointers, overrun bookkeeping, timers, suspend queue, and active operations count.

## Research Notes

This is a mature driver-private contract. Concurrency is split between high-level adaptive locks and high-priority interrupt locks; receive-ring error marking and suspend/resume soft interrupt serialization are key correctness areas.
