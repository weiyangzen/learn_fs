# sources/storage-engines/wiredtiger/test/suite/test_layered_config09.py

Purpose: verifies tiered storage worker startup and tiered object/table creation are disabled in disaggregated storage mode for both leader and follower roles.

Important APIs/types/functions: uses `DisaggConfigMixin`, `disagg_test_class`, role scenarios `leader`/`follower`, URI prefixes `tiered:`, `tier:`, and `object:`, verbose tiered logging, `captureout.checkAdditionalPattern`, and `assertRaisesWithMessage`.

Control flow: connection config enables disaggregated role and `lose_all_my_data=true`. One test checks expected stdout indicating tiered storage was not started because disaggregated storage is active. The create test checks the same message, then attempts to create an object with the selected tiered prefix and expects `Operation not supported`.

State and persistence behavior: no tiered metadata should be created and no tiered worker should run. State under test is startup service gating and create rejection.

Dependencies/integration points: tiered storage subsystem startup, URI-prefix create dispatch, disaggregated mode configuration, and verbose logging.

Risks: log text dependency. Scenario matrix increases coverage but the create body only checks unsupported result, not absence of partial metadata.

Test signals: pass means disaggregated mode suppresses tiered worker startup and rejects tiered/tier/object creates across roles.
