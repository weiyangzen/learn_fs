## sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/sim_validation.h

Purpose: Declares simulator-only durability and version-validation debug hooks for checking restored committed versions and version timestamps after failures.

Important APIs/types/functions: Version range functions include `debug_advanceCommittedVersions()`, min/max advance helpers, `debug_setVersionCheckEnabled()`, `debug_removeVersions()`, `debug_versionsExist()`, and restored version checks for exact/min/max. Relocation-duration toggles are `debug_isCheckRelocationDuration()` and `debug_setCheckRelocationDuration()`. Version timestamp hooks are `debug_advanceVersionTimestamp()` and `debug_checkVersionTime()`.

Control flow: Implementations maintain perfectly durable simulator metadata. Production/non-simulation calls have no effect or validation meaning according to the header comment. Callers advance max before commit, min after commit, and check restored versions after recovery/reboot.

State and persistence behavior: State is simulator magic durable metadata, not normal process memory durability. It models what should survive simulated faults.

Dependencies and integration points: Depends on Flow random UID and trace severity. Used by commit/recovery tests and simulator validation policies.

Risks: Missing advance/check calls can hide durability regressions or produce false failures. Checks are meaningful only in simulation, so production code should not rely on them. Severity choice controls whether validation is fatal or warning-like.

Test signals: Simulated commit/reboot/recovery scenarios, min/max restored version checks, disabled checks, removed version state, relocation-duration toggle, and version timestamp consistency.
