# File Research: sources/os/bsd/freebsd-src/sys/sys/coverage.h

## Purpose
Defines shared kernel coverage comparison metadata and kernel registration hooks for coverage tracing.

## Main Elements
- Userspace must include through `sys/kcov.h`, enforced by a preprocessor error.
- Comparison flags encode constant comparisons and operand size.
- Kernel hook typedefs: program-counter trace and comparison trace callbacks.
- Registration APIs install/uninstall comparison and PC trace callbacks.

## Dependencies And Integration
Used by kernel coverage/KCOV instrumentation paths.

## Risk Notes
The callback interface is global. Registration and unregistration must coordinate with instrumented code paths that can execute on arbitrary CPUs.
