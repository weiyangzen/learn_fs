# sources/object-store/apache-ozone/hadoop-ozone/iceberg/dev-support/findbugsExcludeFile.xml

## Purpose
This SpotBugs/FindBugs exclude file is present for the Ozone Iceberg module.

## Important APIs, types, and functions
It declares an empty `<FindBugsFilter>` root, meaning no module-specific suppressions are currently configured.

## Control flow
No executable behavior is present.

## State and persistence behavior
The file is static build configuration.

## Dependencies and integration points
`iceberg/pom.xml` references this file from the `spotbugs-maven-plugin` configuration.

## Risks and edge cases
An empty filter is useful as a stable plugin path but can hide the fact that no suppressions exist. Future suppressions should be tightly scoped.

## Test signals
SpotBugs execution validates XML parsing and absence/presence of suppressions.
