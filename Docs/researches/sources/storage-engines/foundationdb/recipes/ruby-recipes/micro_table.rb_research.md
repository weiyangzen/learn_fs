<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/ruby-recipes/micro_table.rb -->
# Research: sources/storage-engines/foundationdb/recipes/ruby-recipes/micro_table.rb

## Purpose
Ruby recipe example that implements a two-dimensional table with row and column indexes.

## Important APIs, Types, And Functions
`_pack`, `_unpack`, `table_set_cell`, `table_get_cell`, `table_set_row`, `table_get_row`, `table_get_col`, `clear_subspace`.

## Control Flow
The file selects FoundationDB API version 300, opens the default database, defines transaction-wrapped helper methods, and usually runs an inline smoke scenario. set cell writes both row and column keys, row/column reads scan prefixes, and row replacement clears a row prefix before rewriting cells.

## State And Persistence Behavior
Persistent state duplicates cell values in row and column indexes, so mutations must update both indexes in one transaction.

## Dependencies And Integration Points
Depends on the Ruby FoundationDB binding, tuple/subspace helpers, and a reachable default cluster. Parallels the recipe patterns in Python and Go for documentation and experimentation.

## Risks And Edge Cases
Several files have example-grade issues: fixed global subspaces are cleared, errors are not surfaced, and a few snippets appear to contain typos (`json.loads`, `tr.clear(v)`, `v` variable in `multi_get_counts`, column unpacking from value). They should be read as recipe sketches unless verified.

## Test Signals
Inline smoke output gives manual signal; no automated Ruby test harness is included here.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/ruby-recipes/micro_table.rb -->
