<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/dev-support/findbugsExcludeFile.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/dev-support/findbugsExcludeFile.xml

Purpose: SpotBugs exclude filter for the Recon integration-test module.

Important APIs: XML root `<FindBugsFilter>` with no exclusion rules.

Control flow and integration: referenced by `integration-test-recon/pom.xml` SpotBugs plugin. It provides a stable file path even though no suppressions are currently needed.

State and persistence: static build configuration only.

Risks and tests: no runtime risk. Empty filter means SpotBugs findings are not suppressed locally; future suppressions would need explicit match rules.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/dev-support/findbugsExcludeFile.xml -->
