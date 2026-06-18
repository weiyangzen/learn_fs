# sources/object-store/apache-ozone/hadoop-hdds/server-scm/dev-support/findbugsExcludeFile.xml

Purpose: SpotBugs/FindBugs exclude filter for generated protobuf classes under `org.apache.hadoop.hdds.protocol.proto`.

Important APIs and types: A single `<FindBugsFilter>` with one package `<Match>`, referenced by the server-scm POM's `spotbugs-maven-plugin`.

Control flow: During SpotBugs analysis, findings for the generated protocol package are excluded before reporting.

State and persistence behavior: No runtime state; this is build-time quality-gate metadata.

Dependencies and integration points: Integrates with Maven SpotBugs and generated HDDS protobuf sources.

Risks: Package-level exclusions can hide issues if handwritten code appears in the excluded package; generated-code scope keeps the risk narrow.

Test signals: The build should suppress generated-code findings while still analyzing other server-scm classes.
