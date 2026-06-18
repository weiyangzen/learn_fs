# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ksyms.h

## Purpose
Defines kernel symbol snapshot support for the `ksyms` subsystem.

## Main Interfaces
- Under `_KERNEL`:
  - `ksyms_lock`: reader/writer lock protecting ksyms state.
  - `ksyms_arena`: vmem arena for symbol storage/export.
  - `ksyms_snapshot()`: copies a snapshot through a caller-supplied copy callback.

## Dependencies And Relationships
Includes `sys/kobj.h`, tying ksyms to the kernel runtime linker/module symbol model and vmem infrastructure.

## Research Notes
The copy callback signature lets snapshot code abstract the destination, such as kernel buffer copying or userland-oriented copying.
