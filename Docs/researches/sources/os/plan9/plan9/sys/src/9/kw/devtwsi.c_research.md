# File Research: sources/os/plan9/plan9/sys/src/9/kw/devtwsi.c

## Purpose
Implements the Kirkwood TWSI/I2C device, exposing a `twsi` file for reads and writes to an I2C slave address encoded as the file offset.

## Main Data Structures
- `Kwtwsi`: memory-mapped TWSI controller registers.
- `Twsi`: serialized transfer state: lock, interrupt rendezvous, buffer pointer/range, target address, completion flag, and error string.

## Transfer Flow
- `twsixfer` serializes a transaction with `QLock`, initializes transfer state, asserts START, sleeps for interrupts, advances the read/write state machine, clears interrupt source, reenables interrupts, then returns transferred byte count or raises an error.
- `twsidoread` handles START, slave-read ack, data receive/ack, final no-ack, and abnormal status.
- `twsidowrite` handles START, slave-write ack, data ack, byte transmission, and abnormal status.
- `interrupt` marks an interrupt event, wakes the sleeper, disables further TWSI interrupts until the thread advances state, and clears the interrupt controller source.
- `twsiinit` enables the TWSI interrupt; `twsishutdown` disables it.

## Device Interface
- Device rune is `L'⁲'`; directory contains `twsi`.
- `twsiread` and `twsiwrite` call `twsixfer` with the channel offset as target address.
- `twsiopen`, `twsiwalk`, `twsistat`, and `twsiclose` use standard device helpers.

## Dependencies and Integration
Uses `soc.twsi`, interrupt controller helpers, Plan 9 device plumbing, locks, rendezvous sleep/wakeup, and hardware status codes.

## Risks and Notes
Transfers are strictly serialized globally. Error reporting is coarse (`"abnormal status"`), and the offset-as-address interface makes caller discipline important.
