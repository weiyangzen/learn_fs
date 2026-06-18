# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/keys/KeyUri.java

## Purpose
Ozone shell support type `KeyUri` for key uri behavior. This research is based on a complete read of the 49-line source file.

## Important APIs and Types
Types: `KeyUri`. Important methods: `getValue`, `convert`. CLI parameters: `value`.

## Control Flow
Control flow is minimal: helper/accessor methods return parsed values or construct command objects for the surrounding shell framework.

## State and Persistence
Local state is limited to parsed CLI options, temporary collections, and output formatting. Remote calls are read-oriented unless sibling APIs invoked by the command perform mutation.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.keys` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset.
