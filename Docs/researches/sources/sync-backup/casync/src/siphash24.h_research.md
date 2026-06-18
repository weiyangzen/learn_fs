# sources/sync-backup/casync/src/siphash24.h

Purpose: declares the SipHash state and public hashing helpers.

Important APIs/types/functions: defines `struct siphash` state fields and declares init/write/finalize-style functions for 64-bit keyed hash calculation.

Control flow/state: callers own mutable hash state until finalization. The API is incremental, so large keys/data do not need to be contiguous.

Dependencies/integration: includes integer types and is consumed by `hash-funcs`/hashmap code.

Risks/test signals: the state must not be reused after finalization unless reinitialized. Without visible test vectors in this subset, changes should be checked against standard SipHash-2-4 vectors.

Source research group: `subset-b-009122`.
