# sources/storage-engines/tikv/components/memory_trace_macros/src/lib.rs

## Purpose
This proc-macro implements `#[derive(MemoryTraceHelper)]`, adding `reset` and `sum` methods to structs whose named fields represent memory counters.

## Important APIs, Types, and Functions
- `memory_trace_reset_derive` parses the derive input and emits an inherent impl for the target type.
- For named structs, generated `reset(&mut self, rhs: Self)` sums old and new field values, assigns all fields from `rhs`, and returns `Some(TraceEvent::Sub(delta))`, `Some(TraceEvent::Add(delta))`, or `None`.
- Generated `sum(&self)` returns the sum of all fields.

## Control Flow
The macro accepts only structs with named fields. It iterates over fields twice: once for reset assignment/delta generation and once for sum generation. Non-named fields or non-struct input use `unimplemented!()`, producing a build-time panic rather than a structured compile error.

## State and Persistence Behavior
The generated `reset` mutates the receiver by replacing every field with `rhs` values. It does not persist state outside the receiver.

## Dependencies and Integration Points
Generated code imports `tikv_alloc::trace::TraceEvent` and `std::cmp::Ordering`. The macro is intended for TiKV memory trace structs whose fields are `usize`; the code assumes addition/subtraction is valid for all selected fields.

## Risks
The macro does not type-check fields itself; non-`usize` fields fail later in generated code. Unsupported input shapes panic during macro expansion. The advertised `attributes(name)` is accepted by the derive declaration but not inspected in the implementation, so consumers should not expect field renaming behavior here.

## Test Signals
No local tests are present. Compile-time use sites provide coverage.
