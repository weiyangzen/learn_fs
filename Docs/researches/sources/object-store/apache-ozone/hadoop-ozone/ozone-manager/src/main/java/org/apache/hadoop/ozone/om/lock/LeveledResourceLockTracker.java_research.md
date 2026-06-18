# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/lock/LeveledResourceLockTracker.java

Purpose: `LeveledResourceLockTracker` enforces traditional OM lock-level ordering for `OzoneManagerLock.LeveledResource` values using a per-thread bitset.

Important APIs and types: It is a package-private singleton extending `ResourceLockTracker<OzoneManagerLock.LeveledResource>`. It uses `ThreadLocal<Short> lockSet` and implements `canLockResource`, `getCurrentLockedResources`, `lockResource`, and `unlockResource`.

Control flow: `canLockResource` delegates to the resource's `canLock` method against the current bitset. Locking sets the resource bit before delegating to the base tracker; unlocking clears the bit. Current locked resources are streamed by checking each enum value's bit.

State and persistence behavior: All state is process-local and per-thread. No persistent data is written.

Dependencies and integration points: It supports `OzoneManagerLock` enforcement for volume, bucket, key, user, prefix, and other leveled locks.

Risks and test signals: A single bit per resource cannot represent reentrant hold counts; correctness depends on the surrounding lock implementation and base tracker semantics. Tests should cover lock-order acceptance/denial, reentrant acquire/release behavior, thread isolation, and bitset cleanup after exceptions.
