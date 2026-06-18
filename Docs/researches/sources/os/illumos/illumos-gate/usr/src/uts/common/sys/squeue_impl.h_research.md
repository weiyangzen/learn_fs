# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/squeue_impl.h

## Role

Private implementation header for squeue internals.

## Key Contents

Defines debug/profile compilation controls, default priority, statistics structure, squeue set structure, callback function types, and the full `struct squeue_s`.

The structure contains entry/drain function pointers, lock, state, queue count/head/tail, current running thread, receive ring/ILL association, worker timing and condition variables, CPU binding, worker/poll threads, private storage, set linkage, priority, and debug-only current packet/procedure/connection/tag fields.

## State Flags

Defines processing, worker, enter, fast, user, bound, reenter, polling capability, ILL binding, packet retrieval, default queue, polling, interrupt blanking, forced timer, poll cleanup/quiesce/restart, thread-control, and pause flags.

## Design Notes

The MDB IP module depends on the numeric values of state flags, so flag layout is externally significant to debugging tooling.
