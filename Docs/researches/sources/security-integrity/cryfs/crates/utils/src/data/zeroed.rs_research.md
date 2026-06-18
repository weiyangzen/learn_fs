# sources/security-integrity/cryfs/crates/utils/src/data/zeroed.rs

Purpose: wrapper guaranteeing a mutable byte buffer has been filled with zeroes.

Important APIs/types/functions: `ZeroedData<D>` stores `data: D`; `ZeroedData<Data>::new(len)` allocates zeroed `Data`; generic `fill_with_zeroes(data)` overwrites an existing buffer; `into_inner` returns the buffer.

Control flow: construction either allocates `vec![0; len]` or mutates the supplied buffer with `fill(0)`.

State/persistence: in-memory buffer only. It does not zero on drop; the guarantee is about contents after construction.

Dependencies/integration: useful for security-sensitive buffers where initialized zero contents matter.

Risks: name could be misread as secure memory wiping on drop; it does not provide that. Consuming `into_inner` lets later code mutate bytes.

Test signals: tests cover new length, empty data, zeroing nonzero vectors, and already-zero vectors.
