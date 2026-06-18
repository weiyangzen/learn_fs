# sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigqueueinfo/rt_sigqueueinfo.h

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigqueueinfo/rt_sigqueueinfo.h` is a 17-line LTP source file in the `rt_sigqueueinfo` syscall test area. rt_sigqueueinfo signal delivery coverage for siginfo payloads, threads, and invalid pid/signal/permission cases. Source description: Author: Christian Amann <camann@suse.com>

## Important APIs, Types, and Functions

called APIs/macros: `rt_sigqueueinfo`; local functions: `sys_rt_sigqueueinfo`; important macros/constants: `__RT_SIGQUEUEINFO_H__`.

## Control Flow

Function-level flow is organized around `sys_rt_sigqueueinfo`.

## State and Persistence Behavior

State is process/thread signal state: signal masks, handlers, pending signals, siginfo payloads, and thread ids.

## Dependencies and Integration Points

Direct includes: `"lapi/syscalls.h"`. Depends on LTP `lapi` wrappers for direct syscall numbers, compatibility structures, or missing libc declarations.

## Risks and Edge Cases

signal or child-process synchronization must avoid races

## Test Signals

Build and LTP result output are the primary test signals.
