# sources/sync-backup/kopia/repo/maintenance/maintenance_safety.go

Purpose: defines maintenance safety timing parameters and preset safety levels.

Important APIs/types/functions: `SafetyParameters`, `SafetyNone`, and `SafetyFull`.

Control flow: no functions; the file declares durations for rewrite age, snapshot-GC age/margins, deleted-index drop margin, pack deletion minimum age, session expiration, rewrite-to-orphan-deletion delay, and eventual-consistency behavior.

State/persistence behavior: safety parameters are runtime inputs to maintenance, not persisted by this file.

Dependencies/integration: consumed by content rewrite, snapshot GC, pack GC, index compaction, and full/quick maintenance decisions.

Risks/test signals: `SafetyNone` is intentionally unsafe for concurrent/eventually consistent environments, while `SafetyFull` encodes conservative defaults. Tests in safety and run test files validate practical behavior.
