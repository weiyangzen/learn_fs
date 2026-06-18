<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/plaintext_decision_graph.c -->
# sources/security-integrity/ecryptfs-utils/src/utils/plaintext_decision_graph.c

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/utils/plaintext_decision_graph.c_research.md`. Source lines read for this pass: 43.

## Purpose
Decision-graph node definitions for plaintext/passthrough behavior in the interactive mount option resolver.

## Important APIs, Types, And Functions
Defines `struct param_node plaintext_arr[]` with one mount option name, prompt text, default value, and two yes/no transitions.

## Control Flow
When included in `mount.ecryptfs`, the graph asks whether to enable plaintext passthrough and emits the `passthrough` mount option with value `1` or `0`.

## State And Persistence Behavior
No persistence itself; affects generated mount options.

## Dependencies And Integration Points
Depends on `decision_graph.h` and libecryptfs graph traversal conventions.

## Risks And Edge Cases
Incorrect graph definitions can silently produce insecure mount options such as unintended plaintext passthrough or malformed option names.

## Test Signals
Interactive mount tests should verify user choices map to the expected `ecryptfs_passthrough` option behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/plaintext_decision_graph.c -->
