# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/CodecRegistry.java

## Purpose
`CodecRegistry` is an immutable lookup table for converting typed keys/values to and from persisted byte arrays in HDDS metadata tables.

## Important APIs and Types
`newBuilder` pre-registers codecs for `String`, `Long`, `Integer`, `byte[]`, and `Boolean`. `Builder.addCodec` adds or replaces mappings. `asObject`, `copyObject`, and `asRawData` perform conversion. `getCodec(object)` searches exact class, all superclasses, then all interfaces. `getCodecFromClass` requires an exact registered class.

## Control Flow and State
The registry copies builder mappings into an unmodifiable map. Object lookup allows subclass/interface codecs, while class lookup is stricter. `asRawData` rejects null persisted values with `Objects.requireNonNull`.

## Persistence, Dependencies, and Integration
It has no persistence, but is foundational for typed table persistence. Dependencies include HDDS codec implementations and Apache Commons `ClassUtils`.

## Risks and Test Signals
Subclass/interface search order can pick an unexpected codec when multiple supertypes are registered. `asObject` returns null for null raw data, but `asRawData` rejects null objects. Tests should cover default registry codecs, custom codec overrides, subclass/interface resolution, missing codec errors, null raw/object behavior, and copy semantics for mutable types.
