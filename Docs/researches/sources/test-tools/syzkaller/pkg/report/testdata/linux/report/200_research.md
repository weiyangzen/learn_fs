<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/200 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/200

## Purpose
This fixture validates general protection fault parsing in socket buffer allocation under fault injection. Expected title is `general protection fault in __alloc_skb`, alt `bad-access in __alloc_skb`, type `DoS`, with `CORRUPTED: Y` and `PANICKED: Y`.

## Important APIs, Types, And Functions
The 220-line log includes `FAULT_INJECTION: forcing a failure`, KASAN-enabled GPF text, and panic. Parser features under test include fault-injection noise handling, GPF title extraction, corruption flag, and panic detection. Important frames include `should_fail`, `should_failslab`, `kmem_cache_alloc_node_trace`, `__kmalloc_node_track_caller`, `__kmalloc_reserve.isra.39`, `__alloc_skb`, `skb_copy_and_csum_dev`, plus generic stack dump helpers.

## Control Flow
The Linux reporter should skip the fault-injection prologue as noise, then parse the general protection fault and select `__alloc_skb` from the allocation stack. Runtime flow is network packet buffer allocation/copy under simulated slab allocation failure, followed by fatal exception panic.

## State And Persistence
Static expected state is the title, alt, type, corruption flag, panic flag, and raw log. Dynamic state includes fault-injection counters, allocation flags, memory addresses, and register values.

## Dependencies And Integration Points
It depends on Linux GPF patterns, KASAN-enabled register dump handling, fault injection message filtering, and `DoS` crash-type mapping. It integrates as a report parser regression for corrupted fatal allocation failures.

## Risks
The parser may title from `should_fail` or `kmem_cache_alloc_node_trace`, or classify the report as a sanitizer memory-safety bug despite the expected `DoS` type. Panic and corruption flags must both be preserved.

## Test Signals
Check exact title `general protection fault in __alloc_skb`, alt, type `DoS`, `CORRUPTED: Y`, and `PANICKED: Y`. The selected report should include fault injection context and the `__alloc_skb` frame.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/200 -->
