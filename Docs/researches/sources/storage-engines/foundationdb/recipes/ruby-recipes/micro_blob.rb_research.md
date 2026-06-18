<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/ruby-recipes/micro_blob.rb -->
# Research: sources/storage-engines/foundationdb/recipes/ruby-recipes/micro_blob.rb

## Purpose
Ruby recipe example that stores a large logical value by splitting it into fixed-size chunks keyed by chunk offset.

## Important APIs, Types, And Functions
`clear_subspace`, `write_blob`, `read_blob`, `CHUNK_SIZE`, `@blob`.

## Control Flow
The file selects FoundationDB API version 300, opens the default database, defines transaction-wrapped helper methods, and usually runs an inline smoke scenario. write helpers split non-empty input into chunks and read helpers scan the blob subspace in key order and concatenate values.

## State And Persistence Behavior
Persistent state is one key per chunk in a blob subspace; callers must clear old chunks before overwriting with shorter data or stale chunks can remain.

## Dependencies And Integration Points
Depends on the Ruby FoundationDB binding, tuple/subspace helpers, and a reachable default cluster. Parallels the recipe patterns in Python and Go for documentation and experimentation.

## Risks And Edge Cases
Several files have example-grade issues: fixed global subspaces are cleared, errors are not surfaced, and a few snippets appear to contain typos (`json.loads`, `tr.clear(v)`, `v` variable in `multi_get_counts`, column unpacking from value). They should be read as recipe sketches unless verified.

## Test Signals
Inline smoke output gives manual signal; no automated Ruby test harness is included here.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/ruby-recipes/micro_blob.rb -->
