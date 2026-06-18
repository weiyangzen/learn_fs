# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/container/ReportSubcommand.java

## Purpose
Implements `ozone admin container report`, displaying Replication Manager's container health summary and managing report suppression for specific containers.

## Important APIs, Types, And Functions
Options include mutually exclusive `--suppress/--unsuppress`, `--json`, and `ContainerIDParameters`. `printReport` calls `ScmClient.getReplicationManagerReport`; `handleSuppressUnsuppress` calls `suppressContainers`; output helpers print state summaries, health summaries, and sample container IDs.

## Control Flow
If suppress options are present, the command validates IDs and toggles suppression status. Otherwise it rejects positional IDs, fetches the report, warns when report timestamp is zero, emits JSON or text sections, and prints sample unhealthy containers.

## State And Persistence
Report mode is read-only. Suppress/unsuppress changes SCM report suppression metadata that affects future Replication Manager reports.

## Dependencies And Integration Points
Depends on `ReplicationManagerReport`, `ContainerHealthState`, `ContainerID`, SCM report APIs, and picocli arg groups.

## Risks And Test Signals
Timestamp conversion uses epoch seconds from milliseconds division, losing milliseconds but acceptable for display. Suppression partial failures throw after printing mixed results. Tests should cover no report yet, JSON shape, suppress/unsuppress validation, IDs without suppression, and sample-limit output.
