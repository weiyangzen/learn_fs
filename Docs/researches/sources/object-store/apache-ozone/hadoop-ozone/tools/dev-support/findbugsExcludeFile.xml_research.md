# sources/object-store/apache-ozone/hadoop-ozone/tools/dev-support/findbugsExcludeFile.xml

## Purpose
SpotBugs exclusion filter for the `ozone-tools` module.

## Important APIs, types, and functions
The XML uses `FindBugsFilter` with `Match`, `Class`, and `Bug` pattern entries. It suppresses `OBL_UNSATISFIED_OBLIGATION_EXCEPTION_EDGE` for `TestReconUtils`, plus `RV_RETURN_VALUE_IGNORED_BAD_PRACTICE` and `DLS_DEAD_LOCAL_STORE` for `TestGenerateOzoneRequiredConfigurations`.

## Control flow
Maven SpotBugs reads this file from the module POM and excludes matching findings during analysis.

## State and persistence behavior
No runtime state. It persists static quality-gate policy for known test-code findings.

## Dependencies and integration points
Integrated via `spotbugs-maven-plugin` in `tools/pom.xml`.

## Risks and edge cases
Suppressions can mask real regressions if class names are reused or test behavior changes. One class, `TestReconUtils`, appears outside the visible tools test paths, so the filter may contain legacy or cross-module residue.

## Test signals
The signal is build/static-analysis success without these specific warnings failing the module.
