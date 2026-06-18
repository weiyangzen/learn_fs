# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/dev-support/findbugsExcludeFile.xml

Purpose: this SpotBugs/FindBugs filter file is the module-local exclusion list for the S3 Gateway Maven build.

Important APIs and flow: the XML contains an empty `<FindBugsFilter>` root. Maven's `spotbugs-maven-plugin` references this file from `s3gateway/pom.xml`, so static analysis runs with no module-specific suppressions.

State, dependencies, risks, and tests: there is no runtime state or persistence. The dependency is the SpotBugs plugin's filter schema. The key risk is that future suppressions could hide real S3G defects, but the current empty file is a positive signal. Build/test signal is SpotBugs configuration loading successfully and not excluding any findings for this module.
