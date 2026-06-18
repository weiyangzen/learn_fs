# sources/object-store/apache-ozone/hadoop-ozone/interface-storage/pom.xml

Purpose: Maven descriptor for `ozone-interface-storage`, the module holding OM storage interfaces, helper codecs, lock interfaces/metrics, and generated storage protobuf classes.

Important APIs/types/functions: Configures protobuf compilation for storage protos and SpotBugs exclusion for generated storage proto package. Disables annotation processing via compiler `proc=none`.

Control flow, state, and persistence: Build dependencies expose this module to core OM storage code. It compiles generated proto messages used by persisted metadata and Java interfaces/classes that define OM metadata table access and lock behavior.

Dependencies and integration points: Depends on JCIP annotations, Guava, protobuf Java, Hadoop common, HDDS common/interface/server framework, ozone-common, ozone-interface-client, RocksDB checkpoint differ, and Ratis common. Test dependencies include HDDS common test jar, SCM test jar, and HDDS test utils.

Risks: Since this module defines persistence-facing codecs and protocols, dependency or protobuf changes can affect on-disk compatibility. It also depends on interface-client, so client proto evolution can affect lock metrics proto conversion and tests.

Test signals: Includes focused unit tests for codecs, prefix info immutability/serialization, and DAG lock ordering. Protobuf compilation is part of the module build.
