# sources/object-store/apache-ozone/hadoop-ozone/interface-storage/dev-support/findbugsExcludeFile.xml

Purpose: SpotBugs filter for `ozone-interface-storage` generated storage protobuf classes.

Important APIs/types/functions: Single package-level `<Match>` excludes `org.apache.hadoop.ozone.storage.proto`.

Control flow, state, and persistence: Build-time analysis filter only. It has no runtime effect on OM metadata or generated protobuf code.

Dependencies and integration points: Referenced by `interface-storage/pom.xml` as the SpotBugs exclude filter. It corresponds to generated classes from `OmStorageProtocol.proto`.

Risks: A package-level exclusion can hide findings if non-generated code is later placed in the proto package. If generated package names change, SpotBugs findings may reappear.

Test signals: Static-analysis configuration only; no runtime test signal.
