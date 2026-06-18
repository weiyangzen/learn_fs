# sources/storage-engines/wiredtiger/test/cppsuite/src/util/options_parser.h

## Purpose
Declares minimal command-line option parsing helpers.

## Important APIs, Types, And Functions
`option_exists` checks for an option in `argv`; `value_for_opt` retrieves the following argument as a string.

## Control Flow
The header has no implementation flow; it exposes the parser utilities globally rather than inside `test_harness`.

## State And Persistence Behavior
No state or persistence.

## Dependencies And Integration Points
Includes `<string>`. Used by command-line entry points that need simple option handling.

## Risks And Test Signals
Because functions are global, names may collide in larger binaries. Semantics are intentionally simple and should not be treated as a full option parser.
