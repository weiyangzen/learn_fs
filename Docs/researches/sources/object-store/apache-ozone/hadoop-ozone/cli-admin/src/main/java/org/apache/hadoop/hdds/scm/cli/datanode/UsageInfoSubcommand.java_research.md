# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/UsageInfoSubcommand.java

## Purpose
Implements `ozone admin datanode usageinfo`, showing capacity, usage, reserved, committed, pipeline, and container counts for selected or most/least used datanodes.

## Important APIs, Types, And Functions
Options include required `NodeSelectionArguments` arg group, `--count`, and `--json`. It calls `ScmClient.getDatanodeUsageInfo(hostnameOrIp, nodeId)` for direct lookup or `getDatanodeUsageInfo(mostUsed, count)` for ranking. Nested `DatanodeUsage` converts `DatanodeUsageInfoProto` to printable/JSON fields and percentage getters.

## Control Flow
The command resolves IP/hostname/deprecated address versus node ID, validates count > 0, fetches usage protos, wraps them, then prints JSON or text sections. Text output includes filesystem stats when present and Ozone capacity breakdown always.

## State And Persistence
Read-only against SCM usage state.

## Dependencies And Integration Points
Depends on `NodeSelectionMixin`, SCM usage APIs, `DatanodeDetails`, Jackson serializers, `JsonUtils`, and Hadoop byte formatting.

## Risks And Test Signals
`getOzoneUsedRatio` and `getOzoneAvailableRatio` divide by ozone capacity without zero guard. The arg group allows ranking flags and selectors through inherited options. Tests should cover direct selectors, most/least used, invalid count, zero capacity, filesystem stats absent, JSON decimal serialization, and deprecated `--address`.
