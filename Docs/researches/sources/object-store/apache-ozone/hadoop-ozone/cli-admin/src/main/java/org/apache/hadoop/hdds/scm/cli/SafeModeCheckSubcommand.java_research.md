# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/SafeModeCheckSubcommand.java

## Purpose
Implements `ozone admin safemode status`, including HA-aware querying of a single SCM, a specifically requested SCM, or every SCM node in the configured service.

## Important APIs, Types, And Functions
The command is a picocli `Callable<Void>` with `--all/-a`, `--scm`, and `--service-id` through `ScmOption`. `call()` builds an `OzoneConfiguration`, discovers `serviceId` with `HddsUtils.getScmServiceId`, creates a `ContainerOperationClient` with a mutable `ScmNodeTarget`, and populates `SCMNodeInfo.buildNodeInfo`. Helper methods include `executeForSingleNode`, `findLeaderNode`, `executeForSpecificNode`, `executeForAllNodes`, `queryNode`, `matchesAddress`, and `printSafeModeRules`.

## Control Flow
In HA mode without `--all` or `--scm`, the command asks SCM for roles, parses role strings, matches the leader host or IP to configured SCM client addresses, sets `targetScmNode.nodeId`, and then calls `scmClient.inSafeMode()`. With `--all`, it loops through every `SCMNodeInfo`; with `--scm`, it filters by host or host:port. Verbose mode additionally prints `getSafeModeRuleStatuses()`.

## State And Persistence
The command persists no local state. It mutates the in-memory configuration via `ScmOption`, mutates `ScmNodeTarget` between RPCs, and reads SCM safe mode state and rule status from the cluster.

## Dependencies And Integration Points
It integrates with SCM HA metadata (`SCMNodeInfo`, `ScmNodeTarget`), `ScmClient` safe mode APIs, Ozone CLI error printing, and Apache Commons `StringUtils`/`Pair`.

## Risks And Test Signals
Role parsing depends on colon-delimited `getScmRoles()` strings and may fail if hostnames contain unexpected formatting. `queryNode` catches per-node exceptions and only prints errors, so multi-node failures may still exit successfully. Tests should cover HA leader selection, service ID requirements, `--all`, `--scm` host-only matching, verbose safe mode rule output, and RPC failure behavior.
