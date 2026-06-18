<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/metrics/count_and_size.go -->
## sources/storage-engines/pebble/metrics/count_and_size.go

Purpose: defines the primitive count-plus-byte-size metric used throughout Pebble metrics.

Important APIs and types: `CountAndSize` has `Count` and `Bytes`. Methods include `Inc`, `Dec`, `Accumulate`, `Deduct`, `IsZero`, `Sum`, `String`, and `SafeFormat`.

Control flow: `Inc` increments count and adds file size. `Dec` and `Deduct` use `invariants.SafeSub` for count and byte subtraction, providing assertion/guard behavior against underflow depending on build settings. `Sum` returns a new struct without mutating operands. `SafeFormat` formats as count plus humanized bytes.

State and persistence: pure in-memory value type. It is often embedded inside larger persistent-state-derived metrics, but it does not persist data itself.

Dependencies and integration: used by level metrics, placement metrics, delete pacer, object and file accounting. Depends on `crhumanize`, `invariants`, and `redact`.

Risks and edge cases: arithmetic is unsigned; caller mistakes can underflow in non-invariants behavior depending on `SafeSub` semantics. Formatting omits binary `i` suffix by design, so output stability depends on `crhumanize`.

Test signals: `count_and_size_test.go` covers increment, decrement, accumulate, deduct, non-mutating sum, and zero detection.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/metrics/count_and_size.go -->
