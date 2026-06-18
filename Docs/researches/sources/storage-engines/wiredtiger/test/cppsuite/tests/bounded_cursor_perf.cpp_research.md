# sources/storage-engines/wiredtiger/test/cppsuite/tests/bounded_cursor_perf.cpp

## Purpose
Benchmarks normal versus bounded cursor traversal and bound-setting cost.

## Important APIs, Types, And Functions
`class bounded_cursor_perf : public test` overrides `read_operation`. Static helpers `set_bound_key_lower` and `set_bound_key_upper` apply lower and upper bounds while timing `WT_CURSOR::bound`.

## Control Flow
The read operation asserts a single read thread, compiles bound configuration strings with `WT_CONNECTION::compile_configuration`, creates timers, opens normal next/prev cursors and bounded next/prev cursors, alternates compiled and non-compiled bound application, then advances all cursors. When any cursor reaches `WT_NOTFOUND`, it asserts all reached the end together, resets cursors, and reapplies bounds.

## State And Persistence Behavior
The test is read-only after default population. It records traversal and bound-setting timing metrics through `execution_timer`.

## Dependencies And Integration Points
Depends on `execution_timer`, base test, `connection_manager`, and WiredTiger compiled configuration API. It assumes contiguous populated keys and one collection.

## Risks And Test Signals
The synthetic bounds are outside the key range to keep bounded traversal semantically identical to unbounded traversal. Misconfigured multiple read threads assert. Successful signals are matching end-of-range returns and emitted timing metrics for bounded/default traversal and compiled/non-compiled bound setup.
