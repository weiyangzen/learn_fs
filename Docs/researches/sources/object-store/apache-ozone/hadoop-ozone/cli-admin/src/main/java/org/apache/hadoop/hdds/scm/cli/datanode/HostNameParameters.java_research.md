# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/HostNameParameters.java

## Purpose
Provides hostname list parsing for datanode administrative workflows.

## Important APIs, Types, And Functions
`HostNameParameters` extends `ItemsFromStdin`; `setHostNames` binds required `1..*` host names and `getHostNames` returns the inherited item list.

## Control Flow
Picocli fills the list from command arguments or stdin; decommission, maintenance, and recommission commands pass it to SCM.

## State And Persistence
Hostnames live only for the invocation.

## Dependencies And Integration Points
Used by datanode admin lifecycle commands.

## Risks And Test Signals
No normalization or validation occurs here. Tests should cover missing hostnames, stdin usage, duplicate hosts, and hostnames with ports or unexpected forms as handled by SCM.
