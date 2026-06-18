# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/14

## Purpose

This OpenBSD fixture expects `uvm_fault: rtable_satoplen`. It captures a kernel page fault in route-table prefix-length parsing during route socket output from a `sendto` path.

## Important APIs, Types, and Functions

Reporter behaviors include page-fault recognition, function-specific title extraction from `Stopped at` and DDB trace lines, and DDB context capture. Kernel functions include `rtable_satoplen`, `rtable_lookup`, `rtm_output`, `route_output`, `route_usrreq`, `sosend`, `sendit`, `sys_sendto`, `syscall`, and `Xsyscall`.

## Control Flow

The log starts with a page-fault trap at `rtable_satoplen+0x150`. DDB `show panic` records `kernel page fault`, and the trace shows route message output through a socket send path into route-table lookup. The parser should title the report as a UVM fault in `rtable_satoplen` rather than generic `kernel page fault`.

## State and Persistence Behavior

The fixture stores the faulting virtual address, instruction, registers, process list, locks, malloc stats, and pool stats. The stable persisted research signal is the faulting function; addresses and route buffer values are volatile.

## Dependencies and Integration Points

This integrates OpenBSD page-fault parsing with networking route-socket stack selection. It also uses `show all locks` content that mentions concurrent filesystem locks, which must remain secondary context rather than title input.

## Risks and Edge Cases

The stopped instruction and first trace frame agree on `rtable_satoplen`; losing either can weaken title extraction. Concurrent lock/process noise could mislead a parser that scans all later frames indiscriminately. The title should not include raw fault addresses.

## Test Signals

A passing test returns `uvm_fault: rtable_satoplen` and includes the route-output trace from `rtable_satoplen` through `sys_sendto`.
