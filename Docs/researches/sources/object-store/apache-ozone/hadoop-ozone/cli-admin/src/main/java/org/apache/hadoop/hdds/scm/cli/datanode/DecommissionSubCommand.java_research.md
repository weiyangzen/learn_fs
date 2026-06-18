# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/DecommissionSubCommand.java

## Purpose
Implements `ozone admin datanode decommission`, starting decommission workflows for one or more hostnames.

## Important APIs, Types, And Functions
The command extends `ScmSubcommand`, mixes in `HostNameParameters`, has `--force`, calls `ScmClient.decommissionNodes(hosts, force)`, and shares static `showErrors`.

## Control Flow
It collects hostnames, sends one decommission request, prints all requested hosts, then prints per-node errors and throws `IOException` if SCM reported any failures.

## State And Persistence
It mutates SCM datanode operational state/workflow metadata. Local state is transient.

## Dependencies And Integration Points
Depends on SCM datanode admin APIs, `DatanodeAdminError`, and host parsing via `ItemsFromStdin`.

## Risks And Test Signals
It prints "Started decommissioning" before reporting per-node failures, so users must read stderr. Tests should cover multi-host partial failures, force flag propagation, stdin host lists, and non-zero exit on errors.
