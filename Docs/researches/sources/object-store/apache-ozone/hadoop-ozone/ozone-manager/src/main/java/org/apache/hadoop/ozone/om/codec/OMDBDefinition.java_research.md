# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/codec/OMDBDefinition.java

Purpose: `OMDBDefinition` is the authoritative column-family and codec definition for the OM RocksDB database. It maps every logical OM table to a `DBColumnFamilyDefinition` with key and value codecs.

Important APIs and types: It defines constants and definitions for user, delegation token, S3 secret, volume, bucket, prefix, transaction info, meta, key, deleted, open key, multipart, FSO file/open file/directory/deleted directory, tenant state/access/principal, snapshot info, snapshot renamed, and compaction log tables. `get()` returns a singleton, `getName()` returns the OM DB name, `getLocationConfigKey()` returns the OM DB directory config, and `getAllColumnFamilies()` lists defined CF names.

Control flow: Static initialization constructs each typed column-family definition, builds an unmodifiable map, and initializes the singleton. There is no runtime mutation.

State and persistence behavior: This class defines persistent schema shape, names, and serialization for OM metadata. Changing table names or codecs affects upgrade compatibility and snapshot DB compatibility.

Dependencies and integration points: It is used by OM metadata manager/store initialization, DB tooling, snapshots, compaction logs, and codec validation. It ties to many helper model codecs, `TokenIdentifierCodec`, protobuf codecs, and transaction info codecs.

Risks and test signals: Schema drift is high-risk: missing a new table from `COLUMN_FAMILIES`, changing order-sensitive consumers, or changing codecs can break upgrades and snapshots. Tests should verify all metadata manager table names are represented, `getAllColumnFamilies` contains expected names, old DBs decode correctly, and token/secret/snapshot/tenant tables use compatible codecs.
