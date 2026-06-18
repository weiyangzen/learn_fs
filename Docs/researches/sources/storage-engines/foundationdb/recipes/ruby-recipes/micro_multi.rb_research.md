<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/ruby-recipes/micro_multi.rb -->
# Research: sources/storage-engines/foundationdb/recipes/ruby-recipes/micro_multi.rb

## Purpose
Ruby recipe example that implements a multimap/multiset using atomic add counters.

## Important APIs, Types, And Functions
`multi_add`, `multi_sub`, `multi_get`, `multi_get_counts`, `multi_is_element`, timing helpers.

## Control Flow
The file selects FoundationDB API version 300, opens the default database, defines transaction-wrapped helper methods, and usually runs an inline smoke scenario. add increments a tuple key, subtract decrements or clears at zero, and reads scan an index prefix for members and counts.

## State And Persistence Behavior
Persistent state stores little-endian counters by `(index, value)`; counter encoding and zero cleanup are correctness-sensitive.

## Dependencies And Integration Points
Depends on the Ruby FoundationDB binding, tuple/subspace helpers, and a reachable default cluster. Parallels the recipe patterns in Python and Go for documentation and experimentation.

## Risks And Edge Cases
Several files have example-grade issues: fixed global subspaces are cleared, errors are not surfaced, and a few snippets appear to contain typos (`json.loads`, `tr.clear(v)`, `v` variable in `multi_get_counts`, column unpacking from value). They should be read as recipe sketches unless verified.

## Test Signals
Inline smoke output gives manual signal; no automated Ruby test harness is included here.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/ruby-recipes/micro_multi.rb -->
