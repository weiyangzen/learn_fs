# sources/test-tools/syzkaller/prog/minimization_test.go

Purpose: validates program minimization behavior across deterministic scenarios and randomized invariants.

Important APIs/types/functions: `TestMinimize`, `TestMinimizeRandom`, and `TestMinimizeCallIndex`.

Control flow and state: `TestMinimize` is table-driven and feeds input programs, modes, target call indexes, and custom predicates into `Minimize`, then compares serialized output and resulting call index. Random tests generate programs, track candidate hashes to reject duplicates, randomly accept/reject candidates, and ensure committed output matches the last accepted clone. Call-index tests ensure target call identity survives random minimization.

Dependencies and integration: uses target deserialization/generation, `Minimize`, `Serialize`, `Clone`, `hash.String`, random sources, and Linux/test target descriptions.

Risks: deterministic cases depend on exact serializer output and on the sequence of minimization attempts for unrelated-call pruning. Random tests divide iterations to limit runtime and may miss rare cases.

Test signals: strong coverage for false predicates, removing calls/dependencies, resource defaulting, pointer removal versus pointee minimization, props handling (`fail_nth`, `async`, `rerun`), filename shrinkage, `NoMinimize`, unrelated-call transitive closure, duplicate candidate suppression, and call-index stability.
