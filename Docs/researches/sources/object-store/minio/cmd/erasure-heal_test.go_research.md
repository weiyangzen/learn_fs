# sources/object-store/minio/cmd/erasure-heal_test.go

Purpose: Tests low-level `Erasure.Heal`, independent of full object metadata healing. It verifies shard reconstruction into stale disks under combinations of offline, bad source, and bad destination disks.

Important APIs/types/functions: `erasureHealTests` defines data blocks, disk count, offline/stale disk counts, bad readable disks, bad stale writers, block sizes, object sizes, algorithms, and expected failure. `TestErasureHeal` encodes random data, creates bitrot readers, chooses stale disks by removing readers from one side and writers from the other, injects bad readers/writers, runs `Erasure.Heal`, and compares healed writer checksums against original shard checksums.

Control flow and state: Each case creates a temporary erasure setup, writes source shards, configures stale writer targets, reconstructs through `Heal`, closes readers/writers, and validates checksum parity for successfully healed shards.

Dependencies and integration points: Uses `Erasure.Encode`, `Erasure.Heal`, bitrot readers/writers, filesystem removal for stale target paths, and `badDisk` from encode tests.

Risks: Because this bypasses object metadata, it only validates shard reconstruction and writer behavior, not `xl.meta` correctness or object namespace locks. Failure expectations are sensitive to the number and position of unavailable data versus parity shards.

Test signals: Strong low-level repair coverage, including large object size and non-standard block sizes.
