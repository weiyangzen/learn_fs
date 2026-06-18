# sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/ozone/conf/PrintConfKeyCommandHandler.java

## Purpose
Subcommand handler for printing one trimmed configuration key value.

## Important APIs, types, and functions
Uses picocli `@Parameters(arity="1..1")`, parent `OzoneGetConf`, and `OzoneConfiguration.getTrimmed`.

## Control flow
`call` reads the named key. If present, it prints the trimmed value through the parent output method; if absent, it throws `IllegalArgumentException`.

## State and persistence behavior
Read-only config access. No state persists.

## Dependencies and integration points
Part of the `ozone getconf` command tree and GenericCli error handling.

## Risks and edge cases
Empty strings may be treated as present because only null is rejected. The thrown exception message is user-facing through picocli/GenericCli.

## Test signals
`TestGetConfOptions` asserts both `-confKey` and `confKey` forms print configured SCM names and OM node id.
