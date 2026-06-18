## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/AbstractDatanodeDBDefinition.java

Purpose: Defines the common DBDefinition base for datanode container RocksDB schema definitions.

Important APIs and functions: The constructor stores DB path and configuration. `getName()` returns the DB directory name, `getDBLocation()` returns the parent directory, and `getLocationConfigKey()` intentionally throws because datanode container DBs are located by container/volume paths, not a global config key. Abstract accessors define block data, metadata, and last-chunk column families; finalize blocks is optional.

Control flow and state: This class is immutable after construction, carrying `dbDir` and `config`. Concrete schema definitions supply column family names, codecs, and maps.

Persistence and dependencies: It integrates with HDDS `DBDefinition` and `DBColumnFamilyDefinition` and names the column families consumed by `AbstractDatanodeStore`. It does not itself open RocksDB.

Risks: `getDBLocation()` assumes the supplied path includes a parent directory. Concrete schema definitions must return column families with codecs compatible with existing on-disk data. Optional `getFinalizeBlocksColumnFamily()` returning null requires callers to guard.

Test signals: Instantiate each schema with representative paths, assert DB name/location, verify unsupported location config key, and validate column family definitions and nullability by schema.
