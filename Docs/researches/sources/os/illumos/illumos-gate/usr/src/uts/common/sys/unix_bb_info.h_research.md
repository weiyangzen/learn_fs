# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/unix_bb_info.h

## Purpose
Kernel boot black-box information structure definition.

## Main Interfaces
- Defines `NMI_LEVEL`.
- Defines `struct bb_info` with linked-list pointer and boot/debug metadata fields.

## Dependencies And Relationships
Used by low-level kernel/platform code that records black-box information for diagnostics.

## Research Notes
This is a small diagnostic data structure header; its consumers are platform/kernel internals rather than public APIs.
