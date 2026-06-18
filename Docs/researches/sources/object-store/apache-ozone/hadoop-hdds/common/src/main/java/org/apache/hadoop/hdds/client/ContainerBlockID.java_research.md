## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/client/ContainerBlockID.java

Purpose: immutable pair of container ID and local block ID returned by SCM allocation.

Important APIs: constructor, getters, string append/toString, HDDS protobuf conversion, equality and hash. State/persistence: final primitive fields only.

Dependencies: Jackson `JsonIgnore`, HDDS protobufs. Integration points: `BlockID`, SCM block allocation, container datanode commands, persisted metadata.

Control flow: straightforward serialization/deserialization with no validation. Risks: accepts negative or zero IDs if caller passes them; string format is diagnostic not parseable API. Test signals: protobuf round trip and equality/hash contract.
