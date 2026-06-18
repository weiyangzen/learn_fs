# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestQuotaUtil.java

Purpose: tests quota size calculations for replicated and erasure-coded keys.

Important APIs/types/functions: exercises `QuotaUtil.getReplicatedSize` and `getSizePerReplica` with `RatisReplicationConfig` and `ECReplicationConfig`.

Control flow and state: RATIS factor THREE multiplies logical size by three, while factor ONE leaves it unchanged. EC(3,2) tests cover full stripes, partial stripes within the first data chunk, partial stripes beyond the first chunk, and single-stripe partial data. Per-replica EC size is expected to be replicated size divided by required nodes.

Dependencies and integration points: uses HDDS replication config APIs and one-megabyte EC cell size. These calculations feed bucket/volume quota accounting and snapshot size estimates.

Risks and test signals: catches EC parity overhead miscalculation, especially partial stripe rounding. Incorrect results would affect quota enforcement and storage usage reporting.
