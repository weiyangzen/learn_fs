# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/dev-support/findbugsExcludeFile.xml

Purpose: This SpotBugs/FindBugs filter file is the module-local exclusion hook for `ozone-cli-debug`.

Important APIs and types: It contains a root `<FindBugsFilter>` element with no `<Match>` entries.

Control flow: There is no executable flow; build tooling reads the XML during static analysis.

State and persistence behavior: It persists static-analysis configuration only.

Dependencies and integration points: `cli-debug/pom.xml` points the SpotBugs Maven plugin at this file through `${basedir}/dev-support/findbugsExcludeFile.xml`.

Risks: An empty filter is low risk and means no module-specific warnings are suppressed. Future suppressions should be narrow because this module includes diagnostic tools that interact with local files, SQLite, RocksDB, and Kerberos state.

Test signals: Build/static-analysis behavior is the signal; there are no runtime tests in the file.
