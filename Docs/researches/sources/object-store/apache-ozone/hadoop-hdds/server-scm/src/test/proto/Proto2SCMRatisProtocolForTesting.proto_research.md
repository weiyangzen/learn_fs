# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/proto/Proto2SCMRatisProtocolForTesting.proto

Purpose: This proto2 schema defines a test-only SCM Ratis protocol envelope for serializing method-style requests and responses across different SCM state-machine subsystems.

Important APIs and types: It sets `java_package` to `org.apache.hadoop.hdds.protocol.proto.testing`, `java_outer_classname` to `Proto2SCMRatisProtocolForTesting`, and enables generated equals/hash. `RequestType` enumerates subsystem targets including pipeline, container, block, sequence ID, cert store, move, stateful service config, finalize, secret key, and cert rotate. Messages include `Method`, `MethodArgument`, `ListArgument`, `SCMRatisRequestProto`, and `SCMRatisResponseProto`.

Control flow: There is no executable flow in the schema. Generated code will require `SCMRatisRequestProto.type` and `method`, where `method` contains a method name plus repeated typed byte arguments. Responses contain a required string type and required byte value.

State and persistence behavior: Serialized requests and responses are transient protocol data. Field numbering and required fields are the persistence-sensitive contract if test logs, snapshots, or wire payloads are decoded later.

Dependencies and integration points: The schema integrates tests with protobuf code generation and SCM HA/Ratis request routing. It mirrors production concepts but is isolated under a testing package.

Risks: Proto2 `required` fields make partially populated messages invalid. Adding enum values or fields is generally compatible, but changing field numbers, requiredness, package, or outer class name would break generated-code callers.

Test signals: Protobuf compilation, generated Java availability, and successful serialization/deserialization by SCM Ratis tests.
