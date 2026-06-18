# sources/object-store/apache-ozone/hadoop-hdds/cli-common/dev-support/findbugsExcludeFile.xml

Purpose: SpotBugs/FindBugs exclude filter for the `hdds-cli-common` module.

Important APIs/types/functions: Defines a root `<FindBugsFilter>` with no `<Match>` entries, so it currently excludes nothing.

Control flow: The module POM passes this file to the SpotBugs Maven plugin. SpotBugs reads it during static analysis.

State and persistence behavior: It is static build configuration only.

Dependencies and integration points: Integrated by `hadoop-hdds/cli-common/pom.xml` through `excludeFilterFile`.

Risks: Because the filter is empty, any future need for exclusions must be explicitly added. An empty file is low risk but can mislead readers into thinking there are module-specific suppressions.

Test signals: Static-analysis builds should continue to pass without relying on exclusions from this file.
