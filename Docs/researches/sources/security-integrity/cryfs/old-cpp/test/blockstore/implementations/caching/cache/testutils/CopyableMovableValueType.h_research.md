# sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/testutils/CopyableMovableValueType.h

Purpose: Defines a test value type that is both copyable and movable while tracking live instances. It is used to verify cache templates with less restrictive value requirements than `MinimalValueType`.

Important APIs and types: `CopyableMovableValueType` exposes `instances`, `create(int)`, copy constructor, move constructor, destructor, and `value()`. Construction is private through `create`, which preserves the non-default-constructible property.

Control flow: Copy construction duplicates the integer value and increments the counter. Move construction copies the value, marks the source moved, and also increments the counter for the new object. Destruction decrements the counter.

State and persistence behavior: State is per-object integer value and moved flag plus a process-local atomic live-instance counter.

Dependencies and integration points: Used by cache or queue tests that need a value type satisfying copy and move requirements. It avoids external libraries beyond standard atomics.

Risks: `value()` does not assert moved-from invalidity as strongly as `MinimalValueType`, so it is a weaker misuse detector. The moved-from object's `_isMoved` state is only meaningful while it remains alive.

Test signals: Instance counter returns to zero and copied/moved values preserve the expected integer payload.
