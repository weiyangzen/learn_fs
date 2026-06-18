# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/keyrange.h

## Purpose
`keyrange.h` declares a cheap borrowed-or-owned inclusive range abstraction over two DBT endpoints, including support for infinite endpoints and point-range copy optimization.

## Important APIs, Types, And Functions
Public methods are `create()`, `create_copy()`, `destroy()`, `extend()`, `get_memory_size()`, `get_left_key()`, `get_right_key()`, `compare()`, `overlaps()`, and static `get_infinite_range()`. `comparison` describes positional relationship as `EQUALS`, `LESS_THAN`, `GREATER_THAN`, or `OVERLAPS`.

## Control Flow
The header's contract distinguishes borrowed temporary ranges from copied persistent ranges. Tree nodes use copies, while request/release paths often build borrowed ranges around stack or caller-owned DBTs.

## State And Persistence Behavior
The object stores two DBT copies, two optional endpoint pointers, and `m_point_range`. If endpoint pointers are non-null, accessors return borrowed pointers; otherwise they return the owned DBT copies.

## Dependencies
It depends only on `ft/comparator.h`, which brings DBT and helper declarations. Implementation depends on DBT clone/destroy utilities.

## Integration Points
Every tree operation and lock conflict computation relies on this range relationship contract. Lock escalation uses `extend()` to merge adjacent owned ranges and uses accessors when writing callback buffers.

## Risks And Edge Cases
The enum naming is from the perspective of this range relative to the argument and can be easy to misuse. The type has manual lifecycle functions rather than constructors/destructors, so forgetting `destroy()` leaks copied DBTs.

## Test Signals
Range lock acquisition, release, and escalation provide indirect coverage. Unit tests for overlapping/equal ranges would be valuable because errors here corrupt all higher-level conflict decisions.
