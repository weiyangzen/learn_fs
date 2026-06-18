<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/ruby-recipes/micro_priority.rb -->
# Research: sources/storage-engines/foundationdb/recipes/ruby-recipes/micro_priority.rb

## Purpose
Ruby recipe example that implements a priority queue ordered by tuple keys.

## Important APIs, Types, And Functions
`push`, `next_count`, `pop`, `peek`, `clear_subspace`, `smoke_test`.

## Control Flow
The file selects FoundationDB API version 300, opens the default database, defines transaction-wrapped helper methods, and usually runs an inline smoke scenario. push writes `(priority, sequence, random)` keys, `peek` and `pop` scan one key from the front or back, and pop clears the selected key.

## State And Persistence Behavior
Persistent state is queue entries in priority order; sequence generation uses snapshot/range reads and random suffixes to reduce collisions.

## Dependencies And Integration Points
Depends on the Ruby FoundationDB binding, tuple/subspace helpers, and a reachable default cluster. Parallels the recipe patterns in Python and Go for documentation and experimentation.

## Risks And Edge Cases
Several files have example-grade issues: fixed global subspaces are cleared, errors are not surfaced, and a few snippets appear to contain typos (`json.loads`, `tr.clear(v)`, `v` variable in `multi_get_counts`, column unpacking from value). They should be read as recipe sketches unless verified.

## Test Signals
Inline smoke output gives manual signal; no automated Ruby test harness is included here.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/ruby-recipes/micro_priority.rb -->
