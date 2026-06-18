# File Research: sources/os/linux/linux/fs/dlm/memory.h

## Role

`memory.h` declares DLM memory initialization and typed object allocation/free helpers.

## Interface

It exposes cache lifecycle functions and wrappers for RSB, LKB, LVB, mhandle, writequeue, lowcomms message, and callback allocation.

## Research Notes

Read completely. The declarations match `memory.c` and are used broadly by lock, comms, recovery, and user paths.
