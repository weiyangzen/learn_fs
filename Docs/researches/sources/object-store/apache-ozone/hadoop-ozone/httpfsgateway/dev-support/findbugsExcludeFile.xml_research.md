# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/dev-support/findbugsExcludeFile.xml

## Purpose
This is the SpotBugs/FindBugs exclusion filter for the HttpFS gateway module.

## Important APIs, Types, and Functions
The XML file declares a `<FindBugsFilter>` root with no `<Match>` exclusions.

## Control Flow
There is no runtime control flow. The file is consumed by the Maven SpotBugs plugin.

## State and Persistence Behavior
No application state. It persists static build-tool configuration.

## Dependencies and Integration Points
`pom.xml` points `spotbugs-maven-plugin` at this file through `<excludeFilterFile>${basedir}/dev-support/findbugsExcludeFile.xml</excludeFilterFile>`.

## Risks and Edge Cases
Because the filter is empty, it suppresses nothing. Any future suppression should be reviewed carefully to avoid hiding real gateway bugs.

## Test Signals
Build tooling is the only signal; no unit tests apply.
