# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/schedctl.h

## Role

Private kernel/libc/libsched scheduling-control shared-memory interface header.

## Key Elements

- Defines `sc_public_t`, the user-visible preemption control portion with `sc_nopreempt` and `sc_yield`.
- Defines `sc_shared_t`, the private shared LWP scheduler state used by user-level threading support:
  state, signal-block flag, flags, last CPU, scheduling class ID, class priority, dispatch priority, padding, and preemption-control data.
- Documents that Java has a contract to inspect `sc_state` and `sc_cpu`.
- Defines flags for park, cancellation pending, and EINTR due to cancellation.
- Defines schedctl state values matching kernel thread states except zombie.
- Defines maximum preemption-blocking ticks.
- Under `_KERNEL`, declares schedctl lifecycle, cleanup, preemption/yield setters, class/priority setter, signal-block handling, cancellation, EINTR, and park/unpark helpers.

## Dependencies and Coupling

Includes processor and type definitions for non-assembly consumers. The comment explicitly identifies this as a private interface between system libraries and the kernel.

## Research Notes

Although installed in `sys`, this is not a general public API. Its layout is sensitive because libc/libsched and Java depend on selected fields.
