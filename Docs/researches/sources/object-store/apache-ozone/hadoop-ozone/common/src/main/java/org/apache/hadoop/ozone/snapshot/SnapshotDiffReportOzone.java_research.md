# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/snapshot/SnapshotDiffReportOzone.java

Purpose: Ozone-specific snapshot diff report extending Hadoop HDFS `SnapshotDiffReport` with volume, bucket, and pagination token metadata.

Important APIs and types: Fields `volumeName`, `bucketName`, `token`; static `Codec<DiffReportEntry>`; getters; `toString`; `toProtobuf`/`fromProtobuf`; diff type and entry conversion helpers; `getDiffReportEntry`; and `aggregate`.

Control flow: Construction delegates core diff data to the HDFS parent class and stores Ozone metadata. Protobuf conversion maps diff type enum names and UTF-8 path bytes. `fromProtobuf` reconstructs the snapshot root as an OFS path for `/volume/bucket`. `toString` renders human-readable entries and optional next token. `aggregate` appends another report's diff entries to the current list for paginated aggregation.

State and persistence behavior: The class claims immutability, but `aggregate` mutates the inherited diff list. The delegated codec serializes individual diff entries for DB or protocol storage. Full report persistence is via protobufs in OM snapshot diff APIs.

Dependencies and integration points: Used by snapshot diff server/client responses, OM translator, CLI report rendering, Ozone/HDFS diff model compatibility, and metadata codecs.

Risks: Enum name alignment with protobuf is required. Path conversion assumes UTF-8 and uses raw byte arrays inherited from HDFS. `aggregate` mutability conflicts with immutable documentation and can surprise shared references. `fromProtobuf` creates a fresh `OzoneConfiguration` for OFS path formatting.

Test signals: Round-trip report and entry protobuf conversions, codec encode/decode, token rendering, aggregate behavior, rename entries with target paths, UTF-8 path handling, and OFS snapshot root formatting.
