# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/tenant/TenantShell.java

## Purpose
Picocli/Ozone shell component for `ozone tenant`: Shell for multi-tenant specific operations. This research is based on a complete read of the 41-line source file.

## Important APIs and Types
Types: `TenantShell`. Important methods: `main`.

## Control Flow
Control flow is minimal: helper/accessor methods return parsed values or construct command objects for the surrounding shell framework.

## State and Persistence
Local state is limited to parsed CLI options, temporary collections, and output formatting. Remote calls are read-oriented unless sibling APIs invoked by the command perform mutation.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.tenant` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; shared shell handler/address utilities.

## Risks and Edge Cases
Destructive operations need strong validation because a parsed address or flag mistake can remove server-side data or credentials.

## Test Signals
Tenant/S3 secret behavior should be covered by secure integration tests because mocks cannot prove OM authorization semantics.
