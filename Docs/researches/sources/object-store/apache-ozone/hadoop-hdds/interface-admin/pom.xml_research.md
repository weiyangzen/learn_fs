# sources/object-store/apache-ozone/hadoop-hdds/interface-admin/pom.xml

Purpose: Maven module definition for the HDDS admin interface jar, primarily generated protobuf code.

Important APIs/types/functions: Parent `org.apache.ozone:hdds`, artifact `hdds-interface-admin`, packaging `jar`, properties `maven.test.skip` and `spotbugs.skip`, dependencies `protobuf-java` and `hdds-interface-client`, and build plugins for proto backward compatibility, compiler `proc=none`, and protobuf compilation.

Control flow: Maven builds the module by compiling protobuf sources with `protobuf-maven-plugin`, retaining output directories, skipping tests and SpotBugs because the module has generated code only, and disabling annotation processing in Java compilation.

State and persistence behavior: Build output is generated Java/classes from proto definitions; no runtime state in the POM itself.

Dependencies and integration points: Integrates with common HDDS proto definitions via `hdds-interface-client`, protobuf compiler artifact resolved by `${protobuf.version}` and `${os.detected.classifier}`, and Salesforce proto backwards compatibility plugin.

Risks: Skipping tests and SpotBugs reduces local quality gates. `clearOutputDirectory=false` can preserve stale generated files if proto generation changes unexpectedly. Protobuf plugin depends on OS classifier detection.

Test signals: Build-level signal for generated admin API compatibility and protobuf compilation rather than unit test behavior.
