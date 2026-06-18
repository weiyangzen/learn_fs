# sources/test-tools/syzkaller/executor/_include/flatbuffers/stl_emulation.h

## Purpose

`stl_emulation.h` provides FlatBuffers compatibility aliases and fallbacks for standard-library features across C++ modes. It wraps type traits, `unique_ptr`, optional scalars, and span-like views behind stable `flatbuffers::` names.

## Important APIs, Types, and Functions

Feature macros select `std::optional` and `std::span` when available. Type-trait wrappers include `numeric_limits`, `is_scalar`, `is_same`, `is_floating_point`, `is_unsigned`, `is_enum`, `make_unsigned`, `conditional`, `integral_constant`, `bool_constant`, `true_type`, and `false_type`. `unique_ptr` is an alias or wrapper. Optional support provides `Optional<T>`, `nullopt_t`, `nullopt`, constructors, assignment, `reset`, `swap`, bool conversion, `has_value`, dereference, `value`, `value_or`, and equality operators. Span support provides `dynamic_extent`, fallback `SpanIterator`, `span<T, Extent>`, and `make_span`.

## Control Flow

Preprocessor checks select standard implementations in C++17/C++20-capable environments. Fallback `Optional<T>` stores a scalar and presence flag. Fallback `span` stores pointer and count, enforces fixed extent compatibility at construction, and optionally supports iterators and array/std::array constructors outside minimal mode.

## State and Persistence Behavior

State is value-local. Optional values contain `value_` and `has_value_`; spans are non-owning pointer/count views. `nullopt` is a static or constexpr holder. The header does not allocate by itself.

## Dependencies and Integration Points

It includes `base.h` and standard headers. It is used by FlatBuffers runtime and generated code for optional scalar fields and non-owning byte/element ranges.

## Risks and Edge Cases

Fallback `Optional<T>` is scalar-only. Its optional-to-optional equality for two empty values differs from `std::optional` semantics in this version. Fallback `span` is partial, has unchecked `operator[]`, and fixed-extent mismatch yields an empty span. Minimal mode removes several convenience constructors/iterators.

## Test Signals

Tests should compile under C++11, C++17, and C++20 paths, exercise fallback and standard optional/span, and check generated optional scalar accessors, span construction, fixed extent mismatch, and array/std::array overloads.
