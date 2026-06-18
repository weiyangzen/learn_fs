# sources/object-store/minio/cmd/erasure-healing_test.go

Purpose: End-to-end and edge-case test suite for erasure object healing, including dangling detection, bucket healing, versioned objects, pool selection, corrupted metadata/parts, empty directories, and last-shard reconstruction.

Important APIs/types/functions: `TestIsObjectDangling` table-tests dangling classification under metadata-not-found, corrupt, delete-marker, inline-data, and part-missing scenarios. `TestHealing` and `TestHealingVersioned` verify object metadata/data restoration, stale metadata correction, abandoned data cleanup, and bucket healing. `TestHealingDanglingObject` simulates under-quorum version/delete-marker races and recursive healing with removal. `TestHealCorrectQuorum` verifies healing across multiple pools and meta bucket config objects. `TestHealObjectCorruptedPools`, `TestHealObjectCorruptedXLMeta`, and `TestHealObjectCorruptedParts` corrupt or remove `xl.meta` and part files, then assert repair or deletion. `TestHealObjectErasure` checks whole-object folder loss and unrecoverable quorum loss. `TestHealEmptyDirectoryErasure` covers directory markers. `TestHealLastDataShard` verifies data hashes after reconstructing specific missing data shards across multiple sizes.

Control flow and state: Tests initialize real filesystem-backed erasure object layers, mutate on-disk backend files directly, invoke `HealObject`, `HealObjects`, or `HealBucket`, and then re-read metadata or objects to validate final state. They also manipulate global heal/storage-class state with cleanup defers.

Dependencies and integration points: Exercises the object layer, multipart upload path, versioning metadata system, storage class parity config, direct disk APIs, metadata readers/writers, and madmin heal options. It validates integration between healing, erasure coding, object metadata, and pool routing.

Risks: These tests are expensive and stateful because they use real temp disks and direct filesystem tampering. Some checks rely on exact `FileInfo.Equals` semantics and backend layout names. The versioned test contains subtle equality expectations and is important to watch during metadata-format changes.

Test signals: Very strong coverage for user-visible healing semantics, including recoverable versus unrecoverable corruption and preservation of object bytes after repair.
