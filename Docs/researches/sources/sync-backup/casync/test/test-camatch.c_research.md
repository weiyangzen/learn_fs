# sources/sync-backup/casync/test/test-camatch.c

Purpose: thorough unit test for include/exclude match tree parsing, normalization, subtree inheritance, and matching.

Important APIs/types/functions: builds a match tree from string patterns, asserts child names/types/anchoring/directory flags, normalizes, tests files/directories, checks returned subtrees, and uses `ca_match_equal`.

Control flow/state: creates reference-counted match trees with nested child structures. The test checks both structural parse output and behavioral matching results.

Dependencies/integration: covers `camatch`, glob/path matching, string vectors, and util assertions. It is one of the stronger semantic tests in this subset.

Risks/test signals: pattern order and subtree propagation are subtle; this test guards many edge cases but remains limited to hard-coded patterns.

Source research group: `subset-b-009122`.
