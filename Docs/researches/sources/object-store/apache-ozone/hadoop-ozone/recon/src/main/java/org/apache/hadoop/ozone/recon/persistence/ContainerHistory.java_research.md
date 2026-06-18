## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/persistence/ContainerHistory.java

Purpose: serializable POJO representing historical container replica presence on a datanode.

Important APIs/types/functions: full constructor; default constructor for Jackson; getters/setters for container ID, datanode UUID/host, first/last seen time, last BCS ID getter, state, and data checksum.

Control flow: none beyond property storage.

State and persistence: intended for serialization/deserialization into Recon persistence or API payloads. It carries historical state but no persistence logic itself.

Risks: `lastBcsId` has a getter but no setter, which can limit Jackson or manual mutation after default construction. No validation of timestamps, state, or checksum. Tests should cover Jackson round-trip, constructor values, default-constructor deserialization, and missing setter behavior.
