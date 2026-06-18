# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/2

## Purpose

This OpenBSD fixture expects `pool: double put: mbufpl`. It records a pool allocator panic for a double `pool_put` of an mbuf object during socket receive cleanup.

## Important APIs, Types, and Functions

Reporter behavior includes pool-corruption title extraction, panic parsing, DDB stack handling, and wrapped-line tolerance. Kernel functions include `pool_do_put`, `pool_put`, `m_free`, `m_freem`, `soreceive`, `recvit`, `sys_recvfrom`, `syscall`, and `Xsyscall_untramp`.

## Control Flow

The panic begins at `pool_do_put: mbufpl: double pool_put`, enters DDB, and traces through mbuf free logic while servicing `recvfrom`. Several frame names are split across physical lines, so the parser must keep the stack readable even with console wrapping.

## State and Persistence Behavior

The fixture stores the mbuf address, process metadata, stack addresses, and bug-report footer. The stable title is the allocator class plus pool name `mbufpl`; addresses are volatile.

## Dependencies and Integration Points

This integrates OpenBSD pool allocator diagnostics with network socket receive stack capture. It protects deduplication of mbuf double-free style bugs.

## Risks and Edge Cases

Line wrapping can split `soreceive`, `recvit`, and `sys_recvfrom`, which may confuse frame extraction. The parser should not title this from generic `panic()` or from the user syscall alone.

## Test Signals

A passing test returns `pool: double put: mbufpl`, keeps a non-empty report, and includes the `m_free`/`m_freem`/`soreceive` evidence.
