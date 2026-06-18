# sources/sync-backup/borg/src/borg/chunkers/__init__.py

Purpose: exposes chunker implementations and centralizes chunker factory selection for Borg content chunking.

Important APIs: `get_chunker(algo, *params, **kw)` accepts algorithm name, algorithm parameters, optional `key`, and `sparse`. It derives a 32-bit seed from `key.chunk_seed` for `buzhash`, derives a 32-byte `buzhash64` key from `key.derive_key(..., from_id_key=True)`, instantiates `Chunker`, `ChunkerBuzHash64`, `ChunkerFixed`, or `ChunkerFailing`, and raises `TypeError` for unsupported algorithms.

Control flow and state: no persistent state. The factory translates key material into deterministic chunker seeds so related repositories can preserve chunk boundaries and deduplication behavior.

Dependencies and integration: re-exports reader symbols, imports C/extension-backed buzhash chunkers plus Python fixed/failing chunkers, and depends on key objects implementing `chunk_seed` and `derive_key`.

Risks: changing derivation domains, seed behavior, or default sparse propagation would alter chunk boundaries and deduplication. Unsupported algorithm errors surface wherever `ChunkerParams` values reach this factory.

Test signals: instantiate every algorithm, verify keyless defaults, verify keyed `buzhash64` derivation is called with the documented domain, pass sparse to supported chunkers, and assert unsupported algorithms fail clearly.
