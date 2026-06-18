# sources/object-store/apache-ozone/hadoop-ozone/interface-client/pom.xml

Purpose: Maven module descriptor for `ozone-interface-client`, the jar that publishes Ozone Manager client/admin/inter-service protobuf and gRPC generated Java APIs.

Important APIs/types/functions: The POM is not code, but it defines generation of Java protobuf and gRPC stubs from `src/main/proto`. It runs `protobuf-maven-plugin` goals `compile`, `test-compile`, `compile-custom`, and `test-compile-custom`, with output under `target/generated-sources/proto-java-protobuf-${protobuf.version}` and `grpc-java` as the custom plugin.

Control flow, state, and persistence: Build control is mostly generated-source oriented. It skips tests (`maven.test.skip=true`) and SpotBugs (`spotbugs.skip=true`), disables annotation processing with `maven-compiler-plugin proc=none`, and enables the Salesforce proto backward-compatibility plugin.

Dependencies and integration points: Depends on protobuf Java, gRPC API/protobuf/stub, Guava, HDDS interface-client, Javax annotation API for generated Java 11+ sources, and Netty HTTP/2/proxy runtime jars. Generated artifacts are consumed by Ozone client, OM server, admin CLI, S3, and HA code.

Risks: Proto field-number and enum-value compatibility is the primary risk; the POM includes compatibility tooling, but tests are skipped in this module. gRPC/protobuf plugin version drift can change generated API shape. Excluding `jsr305` from gRPC dependencies avoids dependency conflicts but can surface annotation compatibility issues.

Test signals: Explicitly states there are no tests in the module. Compatibility is expected to be enforced by proto-backwards-compatibility and downstream modules.
