# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/spi/impl/TestKeyPrefixContainerCodec.java

## Purpose
Tests binary encoding for `KeyPrefixContainerCodec`, which persists key-prefix/version/container-id composite keys used by Recon container metadata indexes.

## Important APIs, types, and functions
- Uses singleton `KeyPrefixContainerCodec.get()` as a `Codec<KeyPrefixContainer>`.
- Exercises `toCodecBuffer`, `fromCodecBuffer`, `toPersistedFormat`, `fromPersistedFormat`, `supportCodecBuffer`, and `getTypeClass`.
- Uses `CodecBuffer.Allocator.getHeap`, `KeyPrefixContainer.get` overloads, and `LONG_SERIALIZED_SIZE`.

## Control flow
`testKeyPrefixWithDelimiter` runs multiple prefixes, including underscores and an empty string, through `runTest`. For each case it creates full, key-plus-version, and key-only objects, encodes them to buffers, verifies full decode, verifies shorter buffers are prefixes of the full buffer, compares codec-buffer bytes with persisted-format bytes, and checks expected prefix lengths. Separate tests assert codec-buffer support and type class.

## State and persistence behavior
No external DB is used, but byte layout is persistence-critical. The encoded format must support prefix scans: key-only and key-plus-version encodings must be byte prefixes of the full key/version/container encoding.

## Dependencies and integration points
The codec feeds RocksDB table keys for Recon APIs that map key prefixes to containers and containers to key prefixes. Prefix compatibility is required for range scans by key prefix and version.

## Risks and edge cases
Delimiter-like underscores and empty prefixes guard against ambiguous string parsing. Any change in long serialization size, byte order, or concatenation order can break persisted DB compatibility and prefix scans.

## Test signals
Signals are round-trip equality from buffer and persisted bytes, `startsWith` prefix checks, exact byte-array equality, prefix-length calculations, codec-buffer support, and type-class equality.
