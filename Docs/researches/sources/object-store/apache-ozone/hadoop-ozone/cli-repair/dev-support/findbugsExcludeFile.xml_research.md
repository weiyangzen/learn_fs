# sources/object-store/apache-ozone/hadoop-ozone/cli-repair/dev-support/findbugsExcludeFile.xml

Purpose: This SpotBugs exclude file is the module-local filter for `ozone-cli-repair`.

Important APIs and types: It is an empty `<FindBugsFilter>` document.

Control flow and state: Build-time only; it does not suppress any findings currently.

Dependencies and integration points: The cli-repair `pom.xml` points SpotBugs at this file.

Risks and test signals: Empty filters are low risk but can become a place for accidental broad suppressions later. Build validation should confirm the XML is well-formed and SpotBugs can load it.
