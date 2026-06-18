# sources/test-tools/stress-ng/core-io-uring.c

## Purpose

This file is currently a minimal compile-time integration shim for Linux `io_uring` headers. It includes `config.h` and conditionally includes `<linux/io_uring.h>` when building on Linux with header availability.

## Important APIs, Types, And Functions

No functions or exported symbols are implemented in this file. Its role is to make io_uring header availability part of the build and provide a home for future core io_uring helpers.

## Control Flow

The only control flow is preprocessor gating: Linux plus `HAVE_LINUX_IO_URING_H` includes the kernel header, otherwise the translation unit is effectively empty.

## State And Persistence Behavior

There is no runtime state and no side effect.

## Dependencies And Integration Points

It depends on configure-time feature detection. It integrates with the build system rather than runtime stressor control flow.

## Risks And Test Signals

The main risk is build portability when kernel headers are absent or incompatible. Test signals are successful compilation on Linux with and without `linux/io_uring.h` and on non-Linux platforms.
