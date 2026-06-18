# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/keys/SetAclKeyHandler.java

## Purpose
Picocli/Ozone shell component that replaces ACL entries. This research is based on a complete read of the 53-line source file.

## Important APIs and Types
Types: `SetAclKeyHandler`. Important methods: `getAddress`, `execute`. Mixins: `address`, `acls`.

## Control Flow
Picocli parses options and `Handler` dispatches `execute(...)` with an `OzoneClient` and parsed `OzoneAddress`/object.

## State and Persistence
Local state is limited to parsed CLI options, temporary collections, and output formatting. Remote calls are read-oriented unless sibling APIs invoked by the command perform mutation.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.keys` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities; Ozone ACL object model.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
ACL output behavior is represented by `TestGetAclHandler`; mutation handlers need complementary integration tests. URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset.
