<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/CodecRegistry.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/CodecRegistry.java

## Purpose
`CodecRegistry` is the private singleton registry that maps erasure-code codec names to available raw erasure coder factories. It discovers factories with `ServiceLoader`, orders native implementations before Java implementations, prevents duplicate coder names for the same codec, and exposes lookup methods used by coder creation utilities.

## Important APIs, Types, And Functions
- `getInstance()` returns the eagerly initialized singleton.
- `updateCoders(Iterable<RawErasureCoderFactory>)` registers discovered or test-provided factories and rebuilds the codec-to-coder-name cache.
- `getCoderNames(String codecName)` returns the registered coder-name array for a codec, or `null` if absent.
- `getCoders(String codecName)` returns the registered factory list for a codec, or `null` if absent.
- `getCodecNames()` returns the set of registered codec names.
- `getCoderByName(String codecName, String coderName)` scans a codec's factories for a matching coder name.
- `getCodecFactory(String codecName)` returns the first factory for a codec, effectively the preferred factory, or throws `IllegalArgumentException` if none is registered.

## Control Flow
Class initialization eagerly constructs the singleton, creates empty `HashMap` instances, loads `RawErasureCoderFactory` providers through `ServiceLoader`, and calls `updateCoders`. Registration iterates each factory, groups it by `getCodecName()`, checks for duplicate `getCoderName()` values within that codec, logs conflicts, and skips conflicting entries. Native RS and native XOR factories are inserted at index 0 to make them preferred; other factories append after existing factories. After registration, `coderNameMap` is cleared and rebuilt from `coderMap` so name arrays reflect the current ordering. Lookup methods then read these maps directly.

## State And Persistence
The singleton maintains in-memory mutable maps for the life of the JVM: `coderMap` maps codec names to ordered factory lists, and `coderNameMap` maps codec names to ordered coder-name arrays. There is no durable persistence. `updateCoders` mutates global registry state, which is useful for tests but affects all subsequent lookups in the same JVM.

## Dependencies And Integration Points
The registry depends on Java `ServiceLoader`, SLF4J logging, Guava's `@VisibleForTesting`, HDDS `@InterfaceAudience.Private`, and the `RawErasureCoderFactory` SPI. The service file `META-INF/services/org.apache.ozone.erasurecode.rawcoder.RawErasureCoderFactory` lists RS, XOR, native RS, and native XOR factories. `CodecUtil` uses `getCoderNames` and `getCoderByName` to create encoders/decoders with fallback. Tests in `TestCodecRegistry` verify codec discovery, native-first ordering, duplicate suppression, wrong-codec behavior, and named lookups.

## Risks And Edge Cases
Several lookup methods expose mutable internal data: callers can mutate returned lists or the codec name set, and returned arrays are not defensive copies. `getCoderByName` iterates `getCoders(codecName)` without a null check, so an unknown codec can throw `NullPointerException` instead of returning `null`; current tests only cover wrong coder names for known codecs. `getCodecFactory` also assumes `getCoders(codecName)` is non-null before throwing its own exception, so an unknown codec may not get the intended error path. The singleton maps are plain `HashMap`/`ArrayList` and `updateCoders` is unsynchronized, so concurrent test or plugin registration could race with lookups. The variable `hasConflit` is misspelled, which is cosmetic but lowers readability.

## Test Signals
`TestCodecRegistry` is the main unit-test signal. It checks registered codec names, expected native-first coder order for RS and XOR, `null` for `getCoders("WRONG_CODEC")`, duplicate coder-name suppression via `updateCoders`, and named lookup for all built-in factories. Additional useful tests would cover `getCoderByName` with an unknown codec, `getCodecFactory` with an unknown codec, immutability expectations for returned collections, and repeated `updateCoders` calls in the same JVM.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/CodecRegistry.java -->
