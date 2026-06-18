<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/ruby-recipes/micro_indirect.rb -->
# Research: sources/storage-engines/foundationdb/recipes/ruby-recipes/micro_indirect.rb

## Purpose
Ruby recipe example that demonstrates directory-layer indirection for atomic workspace replacement.

## Important APIs, Types, And Functions
`Workspace#enter`, `#exit`, `#update`, `#current`, `clear_subspace`, `print_subspace`, `smoke_test`.

## Control Flow
The file selects FoundationDB API version 300, opens the default database, defines transaction-wrapped helper methods, and usually runs an inline smoke scenario. a workspace writes to a `new` directory and then removes `current` and moves `new` to `current` inside a transaction.

## State And Persistence Behavior
Persistent state is directory-layer metadata plus data under current/new directories; failures before the move leave old current intact.

## Dependencies And Integration Points
Depends on the Ruby FoundationDB binding, tuple/subspace helpers, and a reachable default cluster. Parallels the recipe patterns in Python and Go for documentation and experimentation.

## Risks And Edge Cases
Several files have example-grade issues: fixed global subspaces are cleared, errors are not surfaced, and a few snippets appear to contain typos (`json.loads`, `tr.clear(v)`, `v` variable in `multi_get_counts`, column unpacking from value). They should be read as recipe sketches unless verified.

## Test Signals
Inline smoke output gives manual signal; no automated Ruby test harness is included here.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/ruby-recipes/micro_indirect.rb -->
