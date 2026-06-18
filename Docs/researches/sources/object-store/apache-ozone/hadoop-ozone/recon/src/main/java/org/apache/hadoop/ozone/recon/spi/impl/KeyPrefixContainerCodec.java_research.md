## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/impl/KeyPrefixContainerCodec.java

Purpose: `KeyPrefixContainerCodec` serializes reverse index keys from key prefix to key version and container ID.

Important APIs and types: singleton `get`, `supportCodecBuffer`, `toCodecBuffer`, `fromCodecBuffer`, `toPersistedFormat`, `fromPersistedFormat`, delimiter helpers, and `copyObject`. Uses `CodecBuffer` for efficient buffered serialization in addition to byte arrays.

Control flow: serialization writes UTF-8 key prefix, optionally `_` plus 8-byte key version, and optionally `_` plus 8-byte container ID. `fromCodecBuffer` supports partial forms by finding delimiters from the end: no delimiter means key-prefix-only; one delimiter means prefix plus version; two delimiters means full key/version/container. `fromPersistedFormat` assumes full form and slices based on fixed trailing long sizes.

State and persistence: no mutable state. The byte format defines RocksDB reverse-index key layout and enables prefix seeks by key prefix and version.

Dependencies and integration points: used by Recon container metadata manager implementations for key-prefix-to-container lookup, particularly APIs that answer which containers hold a key prefix.

Risks and edge cases: delimiter search skips backward by `Long.BYTES`, which is tailored to the binary long suffix layout; malformed data can parse incorrectly. Byte-array deserialization is less flexible than buffer deserialization and expects full entries. `copyObject` returns the same instance.

Test signals: tests should cover buffer and byte-array round trips, partial seek key serialization, key prefixes containing underscores, empty buffer exception, malformed suffixes, and ordering compatibility.
