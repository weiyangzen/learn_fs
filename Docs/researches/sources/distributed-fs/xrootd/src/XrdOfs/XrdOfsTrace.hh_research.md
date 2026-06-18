# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsTrace.hh

## Purpose

`XrdOfsTrace.hh` defines trace macros and trace-bit constants for the OFS layer. It gives OFS and TPC code a common way to emit conditional debug traces through `XrdSysTrace`.

## Important APIs, Types, and Functions

When `NODEBUG` is not defined, macros include `GTRACE`, `TRACES`, `FTRACE`, `XTRACE`, `ZTRACE`, `DEBUG`, and `EPNAME`. In debug-disabled builds they compile to no-ops or zero. Trace flags include directory, open/close, read/write/AIO, exists/chmod/getmode/getsize, remove/rename, sync, truncate, fsctl, stats, mkdir, stat, debug, and checkpoint bits.

## Control Flow

The macros wrap trace emission sites: code defines an endpoint with `EPNAME`, tests a category with `GTRACE`, and emits through `SYSTRACE` only when enabled. In `NODEBUG` builds, related control flow is removed at compile time.

## State and Persistence Behavior

No storage is owned here. Runtime state lives in external `OfsTrace.What` and logger configuration.

## Dependencies and Integration Points

The header includes `XrdSysHeaders`, `XrdSysTrace`, and `XrdOfs.hh` in debug builds. TPC program execution uses `EPNAME`/`DEBUG`; other OFS files use file and operation trace categories.

## Risks and Edge Cases

Macro expressions depend on local variables such as `tident`, `epname`, and sometimes `oh`, so misuse can create compile errors only in debug builds. Some trace bits share values by aliases, which is intentional but can confuse filtering.

## Test Signals

Build both debug and `NODEBUG` configurations. Smoke-test trace categories by enabling `debug`, `open`, `read`, `write`, and `aio` and checking logs appear without changing behavior.
