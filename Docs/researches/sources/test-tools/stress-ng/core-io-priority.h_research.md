# sources/test-tools/stress-ng/core-io-priority.h

## Purpose

This header supplies Linux I/O priority constants when libc does not provide them and declares the ionice parsing and application API.

## Important APIs, Types, And Functions

It defines `IOPRIO_CLASS_RT`, `IOPRIO_CLASS_BE`, `IOPRIO_CLASS_IDLE`, `IOPRIO_WHO_*`, and `IOPRIO_PRIO_VALUE` conditionally. It declares `stress_io_priority_ionice_class_get` and `stress_io_priority_set`.

## Control Flow

Callers parse class names before applying a class/level pair. The macro `IOPRIO_PRIO_VALUE` encodes class and data bits in Linux's expected format.

## State And Persistence Behavior

The header has no state. The implementation mutates process I/O priority where supported.

## Dependencies And Integration Points

It bridges stress-ng option parsing with Linux block scheduler priority APIs.

## Risks And Test Signals

The key compatibility risk is keeping fallback constants aligned with Linux headers. Compile tests against old and new libc/kernel headers are useful.
