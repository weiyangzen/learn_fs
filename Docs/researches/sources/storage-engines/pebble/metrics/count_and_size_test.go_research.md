<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/metrics/count_and_size_test.go -->
## sources/storage-engines/pebble/metrics/count_and_size_test.go

Purpose: unit tests for the primitive `CountAndSize` metric arithmetic.

Important APIs and functions: `expect` is a helper asserting exact count and byte values. Tests cover `Inc`, `Dec`, `Accumulate`, `Deduct`, `Sum`, and `IsZero`.

Control flow: each test initializes a counter, performs one or more operations, and uses `require.Equal` through `expect`. `TestCountAndSize_Sum` also verifies operands are unchanged after summing.

State and persistence: no persistent state; all tests operate on value structs.

Dependencies and integration: depends only on the metrics package and `testify/require`.

Risks and gaps: tests do not exercise underflow or invariants behavior for invalid `Dec`/`Deduct` inputs. Formatting is not directly tested here; placement tests indirectly cover formatted `CountAndSize` output.

Test signals: direct arithmetic coverage ensures the building block used by file, table, blob, and placement metrics behaves predictably.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/metrics/count_and_size_test.go -->
