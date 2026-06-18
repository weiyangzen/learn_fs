# sources/sync-backup/casync/src/siphash24.c

Purpose: implements SipHash-2-4, a keyed hash used for hash table seeding and stable keyed hashing of byte streams.

Important APIs/types/functions: provides state initialization, byte ingestion, finalization, compression rounds, and helper functions declared in `siphash24.h`. It maintains the standard four-word SipHash state and byte count/partial tail handling.

Control flow/state: callers initialize with a 128-bit key, write bytes in chunks, and finalize to a 64-bit result. The implementation processes complete 8-byte lanes and folds remaining bytes plus length during finalization.

Dependencies/integration: used by hash ops and any code needing collision-resistant keyed hashes. It depends on endian-safe utilities for little-endian reads.

Risks/test signals: cryptographic correctness hinges on exact rotation constants, endian packing, and finalization count. Hashmap behavior is an indirect integration test; dedicated known-vector tests would be stronger.

Source research group: `subset-b-009122`.
