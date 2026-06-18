# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/metadata/BigIntegerCodec.java

Purpose: RocksDB metadata codec for `BigInteger` keys, used for certificate serial-number tables in `scm.db`.

Important APIs and types: Singleton `Codec<BigInteger>` with `get`, `getTypeClass`, `toPersistedFormat`, `fromPersistedFormat`, and `copyObject`.

Control flow: Persists a `BigInteger` using Java's standard `toByteArray`; restores using the byte-array constructor. `copyObject` returns the same immutable object.

State and persistence behavior: Stateless singleton. Defines durable key format for `validCerts` and `validSCMCerts` column families.

Dependencies and integration points: Referenced by `SCMDBDefinition` certificate table definitions. Separate from HA message `ScmBigIntegerCodec`.

Risks and test signals: Key ordering and sign representation matter for RocksDB scans. Tests should cover positive serials, large serials, sign-bit-boundary values, and compatibility with existing DB data.
