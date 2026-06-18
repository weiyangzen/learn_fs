## sources/object-store/apache-ozone/hadoop-ozone/freon/dev-support/findbugsExcludeFile.xml

Purpose: SpotBugs/FindBugs exclude filter for the Freon module.

Important APIs/types/functions: root element `<FindBugsFilter>` is empty, meaning no Freon-specific bug patterns are excluded.

Control flow: referenced by `freon/pom.xml` in the `spotbugs-maven-plugin` configuration as `${basedir}/dev-support/findbugsExcludeFile.xml`.

State and persistence behavior: build-time static configuration only.

Dependencies and integration points: integrates with Maven SpotBugs plugin.

Risks: an empty filter is explicit but may surprise maintainers expecting suppressions; any future suppression should be narrowly scoped to avoid hiding Freon command defects.

Test signals: SpotBugs should analyze Freon without module-local exclusions.
