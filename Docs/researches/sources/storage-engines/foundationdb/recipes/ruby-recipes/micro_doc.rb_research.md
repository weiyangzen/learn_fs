<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/ruby-recipes/micro_doc.rb -->
# Research: sources/storage-engines/foundationdb/recipes/ruby-recipes/micro_doc.rb

## Purpose
Ruby recipe example that maps nested JSON/document structures to tuple-addressed leaves.

## Important APIs, Types, And Functions
`to_tuples`, `from_tuples`, `insert_doc`, `get_new_id`, `get_doc`, `clear_subspace`.

## Control Flow
The file selects FoundationDB API version 300, opens the default database, defines transaction-wrapped helper methods, and usually runs an inline smoke scenario. conversion helpers flatten arrays/maps into path tuples, insert assigns or preserves `doc_id`, and retrieval scans a document prefix and reconstructs the object.

## State And Persistence Behavior
Persistent state is one key per document leaf under `(doc_id, path...)`; random ID allocation scans for collisions but is example-grade.

## Dependencies And Integration Points
Depends on the Ruby FoundationDB binding, tuple/subspace helpers, and a reachable default cluster. Parallels the recipe patterns in Python and Go for documentation and experimentation.

## Risks And Edge Cases
Several files have example-grade issues: fixed global subspaces are cleared, errors are not surfaced, and a few snippets appear to contain typos (`json.loads`, `tr.clear(v)`, `v` variable in `multi_get_counts`, column unpacking from value). They should be read as recipe sketches unless verified.

## Test Signals
Inline smoke output gives manual signal; no automated Ruby test harness is included here.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/ruby-recipes/micro_doc.rb -->
