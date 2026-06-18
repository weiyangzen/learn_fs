## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/HddsIdFactory.java

Purpose: simple in-process HDDS long ID generator. Important API: `getLongId()` increments a static `AtomicLong` initialized from `System.currentTimeMillis()`.

Control flow: class initialization creates the counter; every call atomically increments and returns the next value. State/persistence: state is process-local and not persisted. The source comment explicitly warns IDs can collide after restart because the initial value is not durably recorded.

Dependencies: Java concurrency only. Integration points: callers needing cheap temporary or best-effort monotonically increasing IDs. It should not be used for IDs that require cluster uniqueness across process restarts or across machines.

Risks: restart collision, clock rollback relative to previously persisted IDs, and multi-process collision because each JVM owns its own counter. Test signals: verify monotonicity and thread safety under concurrent calls; avoid tests assuming persistence or global uniqueness.
