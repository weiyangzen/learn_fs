# File Research: sources/os/bsd/netbsd-src/sys/sys/once.h

## Purpose
Declares NetBSD one-time initialization/finalization state and helpers.

## Main API
- Type: `once_t`.
- States: `ONCE_VIRGIN`, `ONCE_RUNNING`, `ONCE_DONE`.
- Functions: `once_init`, `_init_once`, `_fini_once`.
- Macros: `ONCE_DECL`, `RUN_ONCE`, `INIT_ONCE`, `FINI_ONCE`.

## Dependencies
Uses `uint16_t` and prediction macros expected from normal system includes.

## Risks and Notes
`RUN_ONCE` fast-paths when status is `ONCE_DONE` and otherwise calls `_init_once`. The structure stores initialization error and reference count, so consumers should propagate the return value.
