# File Research: sources/virtualization/qemu/tools/qemu-vnc/stubs.c

## Purpose
Provides link-time/runtime stubs needed by the standalone `qemu-vnc` binary so it can reuse QEMU UI/VNC code without pulling in full system-emulator subsystems.

## Stubbed Symbols
- `runstate_is_running()` always returns true.
- `phase_check()` always returns true.
- `qdev_find_recursive()` returns NULL.
- Monitor stubs return NULL/false/error, avoiding the generic monitor stub object that would conflict with `qapi_event_emit()`.
- Defines empty `VMStateInfo` objects for migration-related symbols referenced by linked VNC code.

## Filesystem/Storage Relevance
None directly. It supports standalone linking of virtualization UI code.
