<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/ruby-recipes/micro_queue.rb -->
# Research: sources/storage-engines/foundationdb/recipes/ruby-recipes/micro_queue.rb

## Purpose
Ruby recipe example that implements a FIFO queue on ordered tuple keys.

## Important APIs, Types, And Functions
`enqueue`, `dequeue`, `last_index`, `first_item`, `clear_subspace`.

## Control Flow
The file selects FoundationDB API version 300, opens the default database, defines transaction-wrapped helper methods, and usually runs an inline smoke scenario. enqueue finds the last index with a snapshot reverse read and writes the next key with random tie-breaker where available; dequeue reads and clears the first item.

## State And Persistence Behavior
Persistent state is queue entries ordered by index; concurrent enqueue contention and empty queue behavior are example-level concerns.

## Dependencies And Integration Points
Depends on the Ruby FoundationDB binding, tuple/subspace helpers, and a reachable default cluster. Parallels the recipe patterns in Python and Go for documentation and experimentation.

## Risks And Edge Cases
Several files have example-grade issues: fixed global subspaces are cleared, errors are not surfaced, and a few snippets appear to contain typos (`json.loads`, `tr.clear(v)`, `v` variable in `multi_get_counts`, column unpacking from value). They should be read as recipe sketches unless verified.

## Test Signals
Inline smoke output gives manual signal; no automated Ruby test harness is included here.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/ruby-recipes/micro_queue.rb -->
