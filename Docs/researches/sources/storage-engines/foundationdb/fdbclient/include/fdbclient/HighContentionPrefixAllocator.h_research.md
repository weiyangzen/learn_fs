# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/HighContentionPrefixAllocator.h

Purpose: Implements the high-contention prefix allocator used by the directory layer style allocation pattern to choose unique numeric prefixes with low transaction conflict under heavy concurrency.

Important APIs/types/functions: `HighContentionPrefixAllocator` owns `counters` and `recent` subspaces derived from the supplied subspace. Public `allocate()` runs the actor template against a transaction. `windowSize()` grows allocation windows: 64 for starts below 255, 1024 below 65535, then 8192. The private actor reads the highest counter, increments it with `MutationRef::AddValue`, advances windows when half full, samples a random candidate in the current window, writes a marker in `recent`, and adds a write conflict range only on the chosen candidate.

Control flow: Allocation first discovers the current window from the highest counter key. It atomically increments the window counter and reads the count snapshot. If occupancy is too high, it advances the window and clears older counter/recent ranges with `NEXT_WRITE_NO_WRITE_CONFLICT_RANGE`. It then repeatedly samples candidates, writes a no-conflict recent marker, checks whether the current window advanced and whether the candidate was unused, and returns tuple-packed candidate after adding a write conflict on that recent key.

State and persistence behavior: Persistent allocator state lives under the supplied subspace: counter keys by window start and recent keys by candidate. Atomic counter increments are little-endian 8-byte `AddValue` operands. Old windows are cleared as the allocator advances.

Dependencies and integration points: Depends on client boolean params, commit transaction mutations, generated FDB options, subspaces, and Flow unit tests. Used by high-contention directory/prefix allocation code with generic transaction types.

Risks: The code assumes 8-byte counter values; malformed values throw `invalid_directory_layer_metadata`. It relies on no-conflict writes and a final conflict range to reduce contention while preserving uniqueness. Endianness and signed integer interpretation of `AddValue` operands must match FDB atomic op semantics. Random candidate selection can spin under extreme contention.

Test signals: Concurrent allocation uniqueness; window advancement at half-full thresholds; malformed counter value error; old window cleanup; transaction retry behavior; distribution of candidates; tuple-packed prefix compatibility with directory layer consumers.
