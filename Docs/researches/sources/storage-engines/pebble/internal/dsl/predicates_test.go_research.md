# sources/storage-engines/pebble/internal/dsl/predicates_test.go

## Purpose
`predicates_test.go` verifies the most fragile predicate: runtime call stack substring matching.

## Important APIs, Types, And Functions
`TestCallStackIncludes` calls `CallStackIncludes[string]` with a test function name, package path substring, and unrelated function substring.

## Control Flow
The test evaluates predicates immediately from within `TestCallStackIncludes`, expecting matches for `"TestCallStackIncludes"` and `"internal/dsl"` and no match for `"pebble.NewIter"`.

## State And Persistence Behavior
No test state persists. The predicate inspects the current runtime stack each time it evaluates.

## Dependencies And Integration Points
The test uses `crlib/testutils/require` and the generic predicate API. It anchors the behavior relied upon by DSL-driven test probes.

## Risks And Edge Cases
The assertions depend on function naming and path formatting in runtime frames. Heavy compiler inlining or path changes could affect the positive package-path assertion.

## Test Signals
Passing tests signal that stack frames include both function and package substrings and that unrelated substrings are not matched.
