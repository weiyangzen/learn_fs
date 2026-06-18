# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/container/ListSubcommand.java

## Purpose
Implements `ozone admin container list`, streaming container metadata as JSON with filters for ID range, count, lifecycle state, replication type/config, suppression status, and all-container pagination.

## Important APIs, Types, And Functions
Options include `--start`, `--count`, `--all`, `--state`, `--type`, `--replication/--factor`, and `--suppressed`. It parses `ReplicationConfig`, reads `OZONE_SCM_CONTAINER_LIST_MAX_COUNT`, calls `ScmClient.listContainer`, and writes `ContainerInfo` objects with a Jackson `SequenceWriter`.

## Control Flow
If replication is set without type, type defaults to RATIS. Non-`--all` mode caps count to the configured maximum, fetches one batch, writes JSON array entries, and warns if more exist. `--all` mode fetches batches starting after the last returned container ID until empty.

## State And Persistence
Read-only against SCM container metadata. It maintains the current pagination start ID.

## Dependencies And Integration Points
Depends on SCM list APIs, Ozone configuration, Jackson Java time module, `JsonUtils.getStdoutSequenceWriter`, and `ReplicationConfig.parse`.

## Risks And Test Signals
`--all` uses the user count as batch size and does not cap it against SCM maximum; count <= 0 in all mode falls back to max. JSON is the only output shape despite no `--json` option. Tests should cover filters, max-count warning, pagination gaps, suppression tri-state, EC/Ratis replication parsing, and empty results.
