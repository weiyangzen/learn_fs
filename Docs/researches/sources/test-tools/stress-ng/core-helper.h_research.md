# sources/test-tools/stress-ng/core-helper.h

## Purpose

This header exposes stress-ng's general helper API and the `stress_warn_once()` macro. It is the shared declaration point for platform facts, process naming, diagnostics, formatting, sysctl/MSR helpers, and small runtime utilities.

## Important APIs, Types, And Functions

The header declares the exported ASCII tables, CPU and load getters, parent-death and dumpability helpers, timer slack, process name APIs, string munging, zero/null getters, endian checks, build/run info emitters, compiler/uname getters, unimplemented marker, size formatting, option duplication, executable text range and self path lookup, warn-once, unused UID/PID, kernel version, tty width, fork retry, flag permutation, exit-status mapping, BSD sysctl wrappers, x86 MSR reads, sleep/yield helpers, process info dump, machine ID, metric zeroing, zero-buffer check, LD library path preservation, and Linux failure-injection activation.

## Control Flow

The API is intentionally flat and used throughout the codebase. Most functions are safe to call on unsupported platforms because implementation stubs return neutral values, but callers must still check return codes where meaningful.

## State And Persistence Behavior

Several functions mutate process state, global shared memory, kernel controls, or static caches. The header does not own state but exposes APIs whose side effects are significant.

## Dependencies And Integration Points

It includes `stress-ng.h` for project types such as `stress_args_t` and `stress_metrics_t`. The macro `stress_warn_once()` binds call sites to `__FILE__` and `__LINE__`, coupling diagnostics to source locations.

## Risks And Test Signals

Because this is a wide utility header, compatibility is sensitive to prototypes and annotations. Compile coverage across supported platforms and call-site tests for side-effect functions are important.
