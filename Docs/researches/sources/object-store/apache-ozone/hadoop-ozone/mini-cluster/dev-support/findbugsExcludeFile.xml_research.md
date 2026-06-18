# sources/object-store/apache-ozone/hadoop-ozone/mini-cluster/dev-support/findbugsExcludeFile.xml

Purpose: SpotBugs filter for the `ozone-mini-cluster` module.

Important APIs/types/functions: Defines an empty `<FindBugsFilter>`, meaning no module-specific exclusions are currently active.

Control flow, state, and persistence: Build-time static-analysis configuration only.

Dependencies and integration points: Referenced by `mini-cluster/pom.xml` in the SpotBugs plugin configuration.

Risks: Low. The empty file is useful as a stable hook for future exclusions, but adding broad exclusions later could hide test-harness bugs.

Test signals: Static-analysis configuration only.
