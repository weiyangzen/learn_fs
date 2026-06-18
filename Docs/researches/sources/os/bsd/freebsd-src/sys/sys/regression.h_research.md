# File Research: sources/os/bsd/freebsd-src/sys/sys/regression.h

Read completely: 38 lines.

## Purpose
Declares regression-testing-only syscall support for userland.

## Main Elements
- For non-kernel builds, declares `__setugid(int)` as a kernel regression testing syscall interface.
- Contains no kernel declarations.

## Dependencies And Integration
Used by regression tests that need to manipulate or test setugid-related kernel behavior.

## Risk Notes
Small ABI surface. It should remain isolated to testing use; exposing or relying on it in production paths would be inappropriate.
