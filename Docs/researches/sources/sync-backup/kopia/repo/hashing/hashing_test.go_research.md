# sources/sync-backup/kopia/repo/hashing/hashing_test.go

Purpose: validates the shared hashing contract for every registered algorithm.

Important APIs/types/functions: test-local `parameters`, `TestRoundTrip`, `hashing.SupportedAlgorithms`, `hashing.CreateHashFunc`, and `gather.FromSlice`.

Control flow: random inputs and a random secret are generated, then each algorithm hashes one input twice and another input once. The test requires stable output for identical input and differing output for different input.

State/persistence behavior: no repository state; it checks in-memory factory behavior and output-slice handling.

Dependencies/integration: spans all registered hash implementation files because `SupportedAlgorithms` enumerates the registry populated by init functions.

Risks/test signals: catches nil factories, non-deterministic hashing, and failure to use input data. It does not pin golden hashes, so compatible-but-incorrect algorithm changes may pass if they stay deterministic.
