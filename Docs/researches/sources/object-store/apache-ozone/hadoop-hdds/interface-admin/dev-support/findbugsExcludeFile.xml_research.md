# sources/object-store/apache-ozone/hadoop-hdds/interface-admin/dev-support/findbugsExcludeFile.xml

Purpose: SpotBugs/FindBugs exclusion filter for generated admin interface protocol classes.

Important APIs/types/functions: `<FindBugsFilter>` with a single `<Match>` excluding package `org.apache.hadoop.hdds.protocol.proto`.

Control flow: Build tooling reads this filter to suppress static-analysis findings for generated protobuf code.

State and persistence behavior: Static build configuration; no runtime state.

Dependencies and integration points: Integrated with SpotBugs/FindBugs configuration in the Maven module or parent build.

Risks: Broad package exclusion can hide real issues if handwritten code is later placed in the same package. The module POM also sets `spotbugs.skip`, so this filter may be defensive or historical.

Test signals: Static-analysis configuration signal only.
