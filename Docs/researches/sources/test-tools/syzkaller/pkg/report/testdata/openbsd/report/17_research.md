# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/17

## Purpose

This OpenBSD `DoS` fixture expects `panic: attempt to execute user address`. It captures a supervisor-mode attempt to execute address `0xf7` during route cloning in the UDP `connect` path.

## Important APIs, Types, and Functions

Reporter behaviors include panic-title normalization that drops the exact user address, DoS metadata parsing, DDB trace capture, and stack frame filtering around trap helpers. Kernel functions include `pageflttrap`, `kerntrap`, `alltraps_kern_meltdown`, the bogus frame at `0xf7`, `rt_clone`, `rtalloc_mpath`, `in_pcbselsrc`, `in_pcbconnect`, `udp_usrreq`, `sys_connect`, `syscall`, and `Xsyscall`.

## Control Flow

The system panics after trap handling detects an attempted supervisor execution from user space. The trace shows the failing call target before the networking route path, then proceeds through UDP connect. Later DDB output repeats the panic, registers, process table, and locks.

## State and Persistence Behavior

The source preserves the exact attempted address, process IDs, register state, netlock/kernel lock information, and allocator statistics. The title intentionally abstracts the address so different bad user addresses group together.

## Dependencies and Integration Points

This integrates OpenBSD trap/panic parsing with network stack report grouping. It also covers symbolic traces with a non-symbol frame (`f7(...) at 0xf7`) that should be evidence, not the selected title.

## Risks and Edge Cases

Including `0xf7` in the title would fragment reports. Selecting `pageflttrap` or `alltraps_kern_meltdown` would hide the execution-at-user-address condition. The parser must also keep route/UDP frames for triage without treating them as the panic title.

## Test Signals

A passing test returns `panic: attempt to execute user address`, preserves `TYPE: DoS`, and includes the `rt_clone` to `sys_connect` stack.
