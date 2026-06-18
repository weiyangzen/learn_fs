# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/TestOzoneDatanodeShell.java

## Purpose
`TestOzoneDatanodeShell` validates basic picocli behavior for the `ozone datanode` command: empty invocation should parse and run without error, while an unknown option should fail with a clear message.

## Important APIs, Types, and Functions
The test creates a `TestHddsDatanodeService` subclass overriding `start()` to no-op, obtains `HddsDatanodeService.getCmd()`, and parses through `CommandLine.parseWithHandlers(new RunLast(), exceptionHandler, args)`. Custom `IExceptionHandler2` rethrows parse and execution exceptions so assertions can inspect them.

## Control Flow, State, and Persistence
There is no mini cluster and no persisted state. `testDatanodeCommand` invokes with no args and expects no exception. `testDatanodeInvalidParamCommand` invokes `-invalidParam`, expects an exception, unwraps the cause if present, and checks for `Unknown option: '-invalidParam'`.

## Dependencies and Integration Points
This covers command-line parsing for `HddsDatanodeService` without starting the service. It integrates picocli handlers and datanode command wiring.

## Risks and Test Signals
The signal is limited to parser behavior and error text. Risks are brittle message matching and missing coverage for real subcommands or datanode service startup.
