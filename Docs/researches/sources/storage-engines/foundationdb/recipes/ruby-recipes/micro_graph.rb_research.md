<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/ruby-recipes/micro_graph.rb -->
# Research: sources/storage-engines/foundationdb/recipes/ruby-recipes/micro_graph.rb

## Purpose
Ruby recipe example that models directed graph adjacency with forward and inverse indexes.

## Important APIs, Types, And Functions
`set_edge`, `del_edge`, `get_out_neighbors`, `get_in_neighbors`, `clear_subspace`.

## Control Flow
The file selects FoundationDB API version 300, opens the default database, defines transaction-wrapped helper methods, and usually runs an inline smoke scenario. edge setters write both forward and inverse keys, delete clears both, and neighbor reads scan the relevant prefix.

## State And Persistence Behavior
Persistent state duplicates each edge in two subspaces, so both writes must remain transactionally paired.

## Dependencies And Integration Points
Depends on the Ruby FoundationDB binding, tuple/subspace helpers, and a reachable default cluster. Parallels the recipe patterns in Python and Go for documentation and experimentation.

## Risks And Edge Cases
Several files have example-grade issues: fixed global subspaces are cleared, errors are not surfaced, and a few snippets appear to contain typos (`json.loads`, `tr.clear(v)`, `v` variable in `multi_get_counts`, column unpacking from value). They should be read as recipe sketches unless verified.

## Test Signals
Inline smoke output gives manual signal; no automated Ruby test harness is included here.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/ruby-recipes/micro_graph.rb -->
