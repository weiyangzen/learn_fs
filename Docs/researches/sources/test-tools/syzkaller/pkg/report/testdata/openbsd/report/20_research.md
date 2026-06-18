# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/20

## Purpose

This OpenBSD fixture expects `pool: cpu free list modified: mbufpl`. It captures a pool cache magic check failure for the mbuf pool during IPv4 interface address ioctl handling.

## Important APIs, Types, and Functions

Reporter behavior includes pool-cache corruption title extraction, panic parsing, DDB trace capture, and lock/malloc/pool diagnostic handling. Kernel functions include `pool_cache_get`, `pool_get`, `m_get`, `rt_ifa_del`, `in_ioctl_sifaddr`, `in_ioctl`, `ifioctl`, `sys_ioctl`, `syscall`, and `Xsyscall`.

## Control Flow

The allocator detects a modified CPU freelist item while allocating an mbuf. The stack shows route/interface address deletion in response to an ioctl, which needs an mbuf via `m_get`. DDB repeats the panic and trace, then emits locks and allocator state.

## State and Persistence Behavior

The fixture stores the corrupted item address, offset, observed and expected magic values, process metadata, locks, and allocator counters. The title uses the stable pool name `mbufpl` and corruption class, omitting volatile item and magic values.

## Dependencies and Integration Points

This integrates OpenBSD pool-cache diagnostics with networking ioctl stacks. It also tests that `show all locks` content after the crash does not override the allocator-derived title.

## Risks and Edge Cases

The detecting stack may not identify the original corruptor, so over-attributing to `in_ioctl_sifaddr` would be misleading. Numeric magic values should not enter the title. The parser must distinguish this from report 2's double put despite both involving `mbufpl`.

## Test Signals

A passing test returns `pool: cpu free list modified: mbufpl` and includes `pool_cache_item_magic_check`, `m_get`, and `in_ioctl_sifaddr` in the report.
