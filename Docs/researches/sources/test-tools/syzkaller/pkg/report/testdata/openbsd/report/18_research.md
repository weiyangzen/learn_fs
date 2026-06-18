# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/18

## Purpose

This OpenBSD fixture expects generic `uvm_fault`. It captures a kernel page fault at an anonymous executable address before `rt_match` in the UDP connect source-selection path.

## Important APIs, Types, and Functions

Reporter behavior includes generic page-fault title selection when the top frame is an address rather than a named function, DDB transcript parsing, and report-end handling. Kernel functions visible after the anonymous frame include `rt_match`, `in_pcbselsrc`, `in_pcbconnect`, `udp_usrreq`, `sys_connect`, `syscall`, and `Xsyscall`.

## Control Flow

The console records a UVM fault and a stop at raw address `0xfffffd802ea85278`, then DDB repeats `kernel page fault` and traces through route matching and UDP connect. Because the immediate faulting frame is not a stable symbol, the expected title stays generic.

## State and Persistence Behavior

The fixture stores the faulting address, instruction bytes, registers, process table, allocator state, and pool tables. The address is volatile and should not become title material. Parser state should retain the whole report as one crash.

## Dependencies and Integration Points

This integrates OpenBSD page-fault detection with anonymous-frame handling. It complements report 14, where a named route-table function allows a specific `uvm_fault: function` title.

## Risks and Edge Cases

The parser must avoid using raw addresses as titles. It also should not select `rt_match` merely because it is the first named frame after the anonymous address; the expected output documents that this report lacks enough confidence for a function-specific title.

## Test Signals

A passing test returns exactly `uvm_fault`, keeps the anonymous stopped-address line, and includes the route/UDP connect trace as evidence.
