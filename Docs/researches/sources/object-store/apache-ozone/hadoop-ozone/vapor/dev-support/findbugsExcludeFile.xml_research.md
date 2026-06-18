# sources/object-store/apache-ozone/hadoop-ozone/vapor/dev-support/findbugsExcludeFile.xml

## Purpose
SpotBugs exclusion filter for the `ozone-vapor` module.

## Important APIs, types, and functions
Defines an empty `FindBugsFilter`.

## Control flow
SpotBugs reads the file during Maven analysis but no findings are excluded.

## State and persistence behavior
No runtime state.

## Dependencies and integration points
Referenced by the `spotbugs-maven-plugin` configuration in `vapor/pom.xml`.

## Risks and edge cases
An empty filter keeps the module strict, but future suppressions must be added deliberately.

## Test signals
Static-analysis build passes without module-specific suppressions.
