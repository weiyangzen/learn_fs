# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/tenant/TenantListUsersHandler.java

## Purpose
Picocli/Ozone shell component that lists users in a tenant. This research is based on a complete read of the 78-line source file.

## Important APIs and Types
Types: `TenantListUsersHandler`. Important methods: `execute`. CLI options/fields: `prefix` (--prefix/-p), `printJson` (--json/-j). CLI parameters: `tenantId`.

## Control Flow
Picocli parses options and `Handler` dispatches `execute(...)` with an `OzoneClient` and parsed `OzoneAddress`/object. Branching enforces command flags, layout-specific behavior, validation failures, and compatibility fallbacks before mutating the server.

## State and Persistence
Local state is limited to parsed CLI options, temporary collections, and output formatting. Remote calls are read-oriented unless sibling APIs invoked by the command perform mutation.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.tenant` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities; HDDS config/replication helpers; Jackson JSON serialization.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset. Tenant/S3 secret behavior should be covered by secure integration tests because mocks cannot prove OM authorization semantics.
