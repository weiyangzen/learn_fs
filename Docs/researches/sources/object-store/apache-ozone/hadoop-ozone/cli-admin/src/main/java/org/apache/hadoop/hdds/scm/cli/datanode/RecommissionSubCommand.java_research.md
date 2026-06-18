# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/RecommissionSubCommand.java

## Purpose
Implements `ozone admin datanode recommission`, returning decommissioned or maintenance datanodes to service.

## Important APIs, Types, And Functions
The command extends `ScmSubcommand`, mixes in `HostNameParameters`, calls `ScmClient.recommissionNodes(hosts)`, and uses shared `showErrors`.

## Control Flow
It sends all hostnames to SCM, prints a started message for every requested host, then prints per-host errors and throws if SCM reported failures.

## State And Persistence
It mutates SCM datanode operational workflow state.

## Dependencies And Integration Points
Depends on SCM datanode admin APIs and `DatanodeAdminError`.

## Risks And Test Signals
The thrown message says "Some nodes could be recommissioned", likely missing "not". Tests should cover successful recommission, partial failures, stdin host input, and exit status.
