<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/AbstractTester.java -->
# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/AbstractTester.java

## Purpose
`AbstractTester` is the base class for Java binding performance/correctness test programs.

## Important APIs, Types, And Functions
It defines `NUM_RUNS`, ASCII charset, fields for `TesterArgs`, `Random`, `TestResult`, and `FDB`, abstract `testPerformance(Database)`, `runTest`, `run`, `multiVersionDescription`, and `wrapAndPrintError`.

## Control Flow
`run` parses CLI arguments, selects the current test API version, configures multi-version/external-client options, runs the test, catches errors into `TestResult`, and saves results. `runTest` opens the database in a try-with-resources block and calls subclass performance logic.

## State And Persistence Behavior
State includes parsed options, selected FDB API object, random test result collector, and output directory persistence through `result.save`. Database persistence is controlled by subclasses.

## Dependencies And Integration Points
It depends on `FDB`, `Database`, `TesterArgs`, `TestApiVersion`, and `TestResult`. Other test classes extend it for benchmarks and binding validation.

## Risks And Test Signals
Risks include invalid option combinations, external-client configuration order, swallowed parse failures, and result reporting after exceptions. Tests should cover CLI modes, failed `fdb.open`, subclass exception capture, and output serialization.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/AbstractTester.java -->
