## sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/PlatformRandomHelper.java

### Purpose

`PlatformRandomHelper` is a test utility that chooses a `Random` implementation appropriate for 32-bit versus 64-bit platforms.

### Important APIs, Types, And Functions

It exposes `isOs64Bit()` and `getPlatformSpecificRandomFactory()`. The nested `Random32Bit` extends `Random` and overrides `nextLong()` to return a non-negative 32-bit-sized value from `nextInt(Integer.MAX_VALUE)`.

### Control Flow

`isOs64Bit` checks `ProgramFiles(x86)` on Windows and `os.arch` containing `"64"` elsewhere. The factory returns normal `Random` on 64-bit systems and `Random32Bit` on 32-bit systems.

### State And Persistence Behavior

There is no persistent state. The utility affects randomized test inputs, particularly where native `size_t` or Java long values could exceed 32-bit platform limits.

### Dependencies And Integration Points

It depends on JVM system properties and environment variables and integrates with tests that need platform-bounded random values.

### Risks And Edge Cases

- Architecture detection is heuristic and may miss unusual JVM/OS names.
- `Random32Bit.nextLong()` changes the distribution and never returns negative values.
- The class predates newer Java unsigned helpers and exists mainly for JNI size compatibility.

### Test Signals

This file has no tests itself; consumers should verify generated values fit platform constraints. Static research only; no test command was run.
