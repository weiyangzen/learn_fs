# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/util/YamlSerializer.java

## Purpose
`YamlSerializer` is an abstract YAML-backed `ObjectSerializer` for Ozone objects that implement `WithChecksum`. It centralizes loading, saving, checksum verification, SnakeYAML pooling, and conversion of low-level YAML/pool failures into `IOException`.

## Important APIs, Types, And Functions
The class is generic as `YamlSerializer<T extends WithChecksum<T>>` and implements `ObjectSerializer<T>`. Its constructor accepts a Commons Pool `BasePooledObjectFactory<Yaml>` and wraps it in a `GenericObjectPool<Yaml>`.

`load(File)` null-checks the file, opens a `Files.newInputStream`, and delegates to `load(InputStream)`. `load(InputStream)` borrows a pooled `Yaml`, calls `Yaml.load`, rejects an empty YAML document by throwing `IOException`, and returns the deserialized object. `save(File, T)` borrows a `Yaml`, invokes subclass-defined `computeAndSetChecksum`, then writes through `YamlUtils.dump`. `verifyChecksum(T)` reads the stored checksum, copies the object with `copyObject`, recomputes checksum on the copy, and compares the two checksum values. `close()` closes the pool.

The subclass hook is `computeAndSetChecksum(Yaml yaml, T data)`, used by OM snapshot local data code to delegate the object-specific checksum algorithm.

## Control Flow
All YAML operations go through `getYaml()`, which borrows an instance from the pool and returns an `UncheckedAutoCloseableSupplier<Yaml>` whose `close()` method returns the instance to the pool. Try-with-resources in `load`, `save`, and `verifyChecksum` guarantees pool return for normal and exceptional paths after borrowing succeeds.

Save flow mutates the passed object by setting its checksum before dumping it to disk. Verification flow deliberately avoids mutating the input by copying the object before recomputing. Load flow treats `Yaml.load` returning `null` as an error because an empty YAML file would otherwise look like a valid deserialization result with lost snapshot metadata.

## State And Persistence
The persistent output is the YAML file written by `YamlUtils.dump`, including the computed checksum field. Runtime state is limited to the `GenericObjectPool<Yaml>`. The serializer has no explicit synchronization beyond the pool implementation.

## Dependencies And Integration Points
Depends on Apache Commons Pool, SnakeYAML, `YamlUtils`, `ObjectSerializer`, `WithChecksum`, Ratis `UncheckedAutoCloseableSupplier`, SLF4J, and Java file APIs. It is instantiated by Ozone Manager snapshot local data code (`OmSnapshotLocalDataManager`) and tests (`TestOmSnapshotLocalDataYaml`, `TestOmSnapshotLocalDataManager`) with object-specific checksum logic.

## Risks
`save` mutates the supplied object, so callers must not assume the checksum remains unchanged. `load(InputStream)` does not null-check the stream. `verifyChecksum` depends on `copyObject` producing a checksum-independent copy; if a concrete type copies stale checksum state incorrectly, verification can be misleading. The class wraps all load failures as `IOException("Failed to load file", e)`, which can obscure whether the root cause was malformed YAML, type construction, or pool failure. Calling `close()` while other threads are borrowing or using YAML instances would make behavior pool-dependent.

## Test Signals
Useful tests cover round-trip save/load, empty file rejection, missing checksum returning `false`, checksum mismatch returning `false`, successful verification not mutating the original object, pool close behavior, malformed YAML wrapping, and subclass checksum failures. Existing OM snapshot local data tests are the main integration signal.
