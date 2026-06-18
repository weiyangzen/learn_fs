# File Research: sources/os/bsd/freebsd-src/sbin/camcontrol/persist.c

## Purpose
Implements SCSI Persistent Reserve In/Out support for `camcontrol`.

## Main Elements
- Maps persistent-reserve in actions: read keys, read reservation, report capabilities, read full status.
- Maps persistent-reserve out actions: register, reserve, release, clear, preempt, preempt-abort, register-ignore, register-move, replace-lost.
- Maps reservation scopes and types.
- Print helpers:
  - `persist_print_scopetype()`
  - `persist_print_transportid()`
  - `persist_print_res()`
  - `persist_print_keys()`
  - `persist_print_cap()`
  - `persist_print_full()`
- `scsipersist()` parses action, keys, transport IDs, scope, reservation type, APTPL/all-target/spec-I-T flags, unregister, and relative target port.
- Builds appropriate parameter buffers for PERSISTENT RESERVE IN/OUT, including transport ID lists for register/register-move.
- Retries reads with larger allocation lengths when target reports more data than initially allocated.

## Dependencies And Integration
Uses CAM CCBs, SCSI persistent reservation structures/helpers, transport ID parser/formatter, nv lookup helpers, and `sbuf`.

## Risk Notes
Persistent reservation OUT commands alter multi-initiator access control and can block or preempt other hosts. The code intentionally does not over-validate whether keys are required because zero can be valid for some workflows.
