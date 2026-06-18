<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/wal_ut.c -->
# sources/object-store/daos/src/vos/tests/wal_ut.c

## Purpose
`wal_ut.c` is a lower-level BIO WAL unit test suite. It bypasses VOS object operations and constructs fake `umem_wal_tx` transactions to validate WAL reserve, commit, replay, checkpoint, wraparound, large payload, multi-block transaction, and replay-hole behavior against BIO metadata contexts.

## Important APIs, Types, And Functions
`ut_mc_init()` and `ut_mc_fini()` create/open and close/destroy a BIO metadata context through `bio_mc_create()`, `bio_mc_open()`, `bio_mc_close()`, and `bio_mc_destroy()`. `struct ut_fake_tx` stores generated `umem_action` arrays, payload buffer, action indexes, payload size, and copy-pointer sizing. `ut_fake_wal_tx_ops` supplies `wtx_act_nr`, `wtx_payload_sz`, `wtx_act_first`, and `wtx_act_next` so `bio_wal_commit()` can serialize the fake transaction as if it came from UMEM.

`ut_tx_add_action()` generates `UMEM_ACT_COPY`, `UMEM_ACT_COPY_PTR`, `UMEM_ACT_ASSIGN`, `UMEM_ACT_MOVE`, `UMEM_ACT_SET`, `UMEM_ACT_SET_BITS`, and `UMEM_ACT_CLR_BITS` actions. `ut_replay_one()` validates replayed actions byte-for-byte, normalizing `COPY_PTR` replay to a `COPY` action with embedded payload. `ut_tx_array` and `ut_replay_multi()` track ordered replay of many transactions.

## Control Flow
Each test creates a 128 MiB meta/WAL/data context, commits one or more fake transactions with `bio_wal_reserve()` and `bio_wal_commit()`, closes and reopens the metadata context, then calls `bio_wal_replay()` with a validation callback. `wal_ut_single()` covers all supported action types. `wal_ut_many_acts()` sizes a transaction to span two and a half WAL blocks. `wal_ut_large_payload()` commits multiple 1 MiB copy-pointer payloads.

`wal_ut_multi()` commits ten transactions and verifies replay order and full action consumption. `wal_ut_checkpoint()` checkpoints at the midpoint and expects only transactions after the checkpointed ID to replay. `wal_ut_wrap()` and `wal_ut_wrap_many()` use `ut_fill_wal()` to fill and checkpoint enough large transactions to force WAL wraparound before replaying the final batch. `wal_ut_holes()` uses `DAOS_NVME_WAL_TX_LOST` fault injection and unmap support to simulate dropped transactions and verify replay skips holes until they are filled.

## State And Persistence Behavior
The persistent state under test is the WAL stream and its header/checkpoint metadata in BIO-managed blobs. Transaction IDs returned by `bio_wal_reserve()` are stored in fake transaction objects and compared during replay. Checkpointing via `bio_wal_checkpoint()` returns a non-zero purge size and advances the replay starting point. Wrap tests ensure old checkpointed WAL ranges can be reused without corrupting later replay.

The fake transaction payload buffer is rendered deterministically and referenced by copy-pointer actions; replay must persist the pointed-to data as inlined copy payload. `UMEM_ACT_CSUM` is explicitly unsupported in this unit test because BIO unit tests self-poll and do not model delayed NVMe checksum completion.

## Dependencies And Integration Points
The file depends on `bio_ut.h`, `bio_wal.h`, BIO metadata context setup from `ut_init()`/`ut_fini()`, cmocka, DAOS allocation/logging/fault-injection utilities, and SMD/NVMe behavior such as unmap support. `run_wal_tests()` registers the suite under a BIO unit-test setup/teardown pair, distinct from the VOS-level WAL suite of the same exported name in another test module.

## Risks And Edge Cases
The fake transaction object casts into `umem_wal_tx.utx_private`, so size/layout compatibility with the private area is assumed. Random action contents are seeded from `ut_args.bua_seed`, making tests deterministic only if setup initializes that seed consistently. Hole tests are skipped on devices without unmap support. Large payload and wrap tests consume significant memory and WAL capacity but are bounded by 128 MiB contexts and 800 KiB per large transaction.

## Test Signals
Strong signals include exact replayed action equivalence, replay action count matching commit action count, multi-transaction replay ordering, post-checkpoint replay count equal to transactions after the checkpoint, non-zero checkpoint purge size, wraparound replay of the most recent batch only, and no replay from WAL holes until a later transaction fills the missing position.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/wal_ut.c -->
