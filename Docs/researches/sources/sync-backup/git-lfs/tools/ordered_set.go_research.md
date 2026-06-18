# sources/sync-backup/git-lfs/tools/ordered_set.go

Purpose: insertion-ordered unique string set.

Important APIs/types/functions: `OrderedSet`, constructors, `Add`, `Contains`, `ContainsAll`, `IsSubset`, `IsSuperset`, `Union`, `Intersect`, `Difference`, `SymmetricDifference`, `Clear`, `Remove`, `Cardinality`, `Iter`, `Equal`, and `Clone`.

Control flow: maintains slice order plus map from value to index. Set operations build new ordered sets, preserving receiver order where relevant. `Iter` launches a goroutine to emit elements.

State and persistence: in-memory slice/map only; not concurrency-safe.

Dependencies and integration points: internal utility for deterministic ordered membership. Uses built-in `min`.

Risks: `Remove` has subtle index/slice math and must keep map indexes synchronized. `Iter` can leak a goroutine if the caller does not drain the channel. `Equal` compares index maps, so order matters.

Test signals: `ordered_set_test.go` covers all major operations, ordering, equality, and cloning.
