# sources/storage-engines/pebble/internal/keyspan/defragment_test.go

## Purpose
Validates `DefragmentingIter` across scripted and randomized operation sequences, including equality method choices, key reducers, error injection, and direction changes.

## Important APIs, Types, And Functions
`TestDefragmentingIter` runs `testdata/defragmenting_iter` with `DefragmentInternal`, an `alwaysEqual` method, `StaticDefragmentReducer`, and a collecting reducer that appends and sorts keys. `TestDefragmentingIter_Randomized` and `_RandomizedFixedSeed` generate spans, fragment them with `Fragmenter`, and compare histories. Helper `fragment` sorts by start key and builds fragments; `debugContext` emits a unified diff on failure.

## Control Flow
The datadriven test defines spans, attaches optional probes, initializes a defragmenting iterator, then runs each requested iterator operation. The randomized test creates logical spans, splits each into random physical fragments, fragments both sets canonically, and executes weighted random operations against reference and fragmented iterators.

## State And Persistence Behavior
The tests keep local span slices and history buffers only. Random seeds are logged for reproduction; no external state is written.

## Dependencies And Integration Points
Depends on package-local `Fragmenter`, `NewIter`, `ParseSpan`, `RunIterOp`, probe DSL helpers, `testkeys`, `datadriven`, and `go-difflib`.

## Risks And Edge Cases
The randomized generator focuses on range-key sets with short alphanumeric keyspaces and may not cover every range key kind or suffix/value mix. The fixed seed is useful but not exhaustive.

## Test Signals
Failures indicate logical defragmentation diverges from unfragmented reference behavior, especially around seeks into the middle of fragmented spans, direction switches, reducer ordering, or child errors.
