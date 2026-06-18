# Research: sources/object-store/minio/cmd/bucket-lifecycle_test.go

Purpose: unit tests lifecycle helper logic that can be exercised without a full HTTP handler path: restore status parsing, restore status serialization, restored-object presence decisions, remote-object detection, and transition tier validation.

Important APIs and tests: `TestParseRestoreObjStatus` checks valid completed and ongoing `x-amz-restore` header forms and invalid combinations. `TestRestoreObjStatusRoundTrip` verifies `restoreObjStatus.String()` can be parsed back. `TestRestoreObjOnDisk` checks expiry-based `OnDisk`. `TestIsRestoredObjectOnDisk` checks metadata map interpretation. `TestObjectIsRemote` checks both `FileInfo.IsRemote` and `ObjectInfo.IsRemote`. `TestValidateTransitionTier` parses lifecycle XML and tests nonexistent storage class rejection.

Control flow: each test defines table cases and compares exact return values. `TestObjectIsRemote` creates valid `FileInfo`, marks transition status complete for metadata cases, converts to `ObjectInfo`, and finally verifies a non-transitioned object is not remote. Tier validation resets `globalTierConfigMgr` and parses lifecycle XML before invoking `validateTransitionTier`.

State and persistence behavior: no persistent state is written. The only global mutation is replacing `globalTierConfigMgr` in the tier validation test.

Dependencies and integration points: depends on lifecycle XML parsing, MinIO HTTP constants, `FileInfo`/`ObjectInfo` conversion, restore header time formatting, and tier config manager behavior.

Risks: tests using `time.Now().Add(...)` rely on immediate evaluation and could become flaky only under extreme clock or scheduling issues. The transition tier test covers rejection and no-transition success but not a configured valid transition target.

Test signals: good focused coverage for restored/remote state interpretation, including expired restored copies. It does not cover restore request XML validation, transition object execution, background queues, or audit tag generation.
