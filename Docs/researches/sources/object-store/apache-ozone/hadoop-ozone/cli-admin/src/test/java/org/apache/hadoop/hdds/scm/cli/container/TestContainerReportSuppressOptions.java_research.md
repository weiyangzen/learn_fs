<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/container/TestContainerReportSuppressOptions.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/container/TestContainerReportSuppressOptions.java

Purpose: Tests container report suppression and unsuppression flows: showing health counts, suppressing missing containers, listing suppressed/non-suppressed containers, and rejecting invalid argument combinations.

Important APIs and types: `ReportSubcommand`, `ListSubCommand`, mocked `ScmClient`, `ReplicationManagerReport`, `ContainerID`, `ContainerInfo`, `LifeCycleState`, container health states, `suppressContainers`, `listContainer`, Picocli, and captured stdout/stderr.

Control flow: Setup creates a mock SCM client that returns a report with empty/missing counts, list-container results that distinguish suppressed and all entries, and successful suppress/unsuppress calls. Tests parse command args for normal report, `--suppress`, `--unsuppress`, list suppressed, list non-suppressed, and invalid container IDs without suppress flags. Each command is executed directly against the mock.

State and persistence behavior: Persistent SCM suppression state is modeled by mock collections. Test state includes constructed container lists and report objects; no real SCM metadata is changed.

Dependencies and integration points: Covers interaction between report and list container CLI commands and SCM suppression APIs, including the user-visible effect of suppressed missing containers on report counts.

Risks: The test class uses ordered tests and mutable mocked report/list setup, which can hide inter-test coupling. Output assertions mostly check substrings rather than full JSON/table structure.

Test signals: Report shows `EMPTY: 1` and `MISSING: 1`; suppress prints `Suppressed container: 2`; subsequent report shows missing zero; unsuppress restores missing; list outputs include or exclude container IDs and `suppressed` JSON fields; invalid IDs without suppress/unsuppress throw `ParameterException`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/container/TestContainerReportSuppressOptions.java -->
