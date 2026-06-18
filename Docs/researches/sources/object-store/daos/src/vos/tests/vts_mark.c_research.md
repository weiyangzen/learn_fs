# sources/object-store/daos/src/vos/tests/vts_mark.c

## Purpose
`vts_mark.c` tests `vos_obj_mark_corruption` and the behavior of VOS after marking objects, dkeys, or akeys as corrupted. It verifies validation errors, propagation of `-DER_DATA_LOSS` to fetch/update/punch, allowed repeated marks, behavior for nonexistent targets, discard and aggregation interactions, and direct delete behavior used by DDB-style repair flows.

## Important APIs, Types, And Functions
`vts_mark_update` is the main setup helper. It optionally creates a new object and dkey, generates dkey/akey/value buffers, configures a single-value IOD, and performs `vos_obj_update`. `vts_mark_prep_sgl` prepares a one-iov scatter/gather list for reads or writes. The test bodies are `vts_mark_1` through `vts_mark_5`, with `vts_mark_discard` and `vts_mark_delete` as reusable scenario helpers.

## Control Flow
`vts_mark_1` covers object-level corruption. It first verifies invalid argument combinations, marks an existing object corrupted, confirms fetch/update/punch return `-DER_DATA_LOSS`, repeats the mark successfully, then marks a nonexistent object and verifies it becomes a corrupted object visible to data-loss checks.

`vts_mark_2` covers dkey corruption. It rejects invalid empty or null dkeys, marks an existing dkey, checks data-loss errors on fetch/update/punch for that dkey, proves another dkey under the same object still works, and marks a nonexistent dkey successfully.

`vts_mark_3` covers akey corruption. It rejects invalid akeys, marks multiple akeys including a nonexistent one, confirms corrupted akeys reject fetch/update/punch, and proves a separate akey under the same dkey remains readable.

`vts_mark_4` calls `vts_mark_discard` for object, flat KV key, and integer akey cases. The helper marks corruption, asserts forced aggregation fails with `-DER_DATA_LOSS`, then discards the object or dkeys and verifies existence-check fetch returns `-DER_NONEXIST`. `vts_mark_5` calls `vts_mark_delete` for corrupted object, dkey, and akey deletion and confirms direct delete/key-delete removes the target.

## State And Persistence Behavior
The tests create persistent VOS object tree entries, mark corruption at different hierarchy levels, and verify that corruption state blocks normal IO until discard or delete removes it. `vts_mark_discard` uses epoch ranges and forced aggregation flags to prove aggregation refuses to merge corrupted state, while `vos_discard` can clear it. The flat KV case expects akey-level corruption to fail with `-DER_NO_PERM` and then falls back to dkey-level corruption.

## Dependencies And Integration Points
The file depends on DAOS common/VOS types and the shared `vts_io.h` fixture. It integrates with CMocka through `mark_tests` and `run_mark_tests`, using `setup_io` and `teardown_io`. It exercises VOS APIs `vos_obj_update`, `vos_obj_fetch`, `vos_obj_punch`, `vos_obj_mark_corruption`, `vos_aggregate`, `vos_discard`, `vos_obj_del_key`, and `vos_obj_delete`.

## Risks And Test Signals
The tests encode exact error-code contracts for corrupted data paths. A risk is that they rely on sleeps around aggregation/discard, which can add runtime and may hide timing assumptions. Strong signals include `-DER_INVAL` for invalid mark arguments, `-DER_NO_PERM` for flat akey marks, `-DER_DATA_LOSS` while corruption exists, successful repeat and nonexistent-target marking, and `-DER_NONEXIST` after discard/delete.
