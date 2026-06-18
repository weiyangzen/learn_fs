# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/contract/AbstractFSContractTestBase.java

Purpose: `AbstractFSContractTestBase` is the shared JUnit 5 base class for all filesystem contract tests in this package. It creates and initializes the concrete `AbstractFSContract`, exposes the test `FileSystem`, scopes paths to the contract test root, handles setup/teardown cleanup, and centralizes common assertions and exception policy.

Important APIs/types/functions: implements `ContractOptions`; uses `Configuration`, `FileSystem`, `Path`, `FileStatus`, `TestInfo`, AssertJ assumptions/assertions, SLF4J, and `ContractTestUtils`. Key members are `contract`, `fileSystem`, `testPath`, and `testMethodName`. Important methods include `createContract(Configuration)`, `createConfiguration()`, `setup()`, `teardown()`, `deleteTestDirInTeardown()`, `path`, `methodPath`, `absolutepath`, `skipIfUnsupported`, `isSupported`, `assumeEnabled`, `handleRelaxedException`, `handleExpectedException`, file/directory assertions, `mkdirs`, `assertDeleted`, `assertMinusOne`, `rename`, and `generateAndLogErrorListing`.

Control flow: a `@BeforeAll` names the initial thread. A `@BeforeEach` using `TestInfo` records the current test method name and names the thread. The public `setup()` creates a configuration, constructs and initializes the contract, assumes it is enabled, obtains the filesystem, verifies URI scheme matches the contract scheme to prevent accidental local filesystem use, computes the test path, and creates it. `teardown()` deletes the test directory and invokes contract teardown.

State and persistence behavior: the base class owns per-test filesystem state under `testPath` and ensures cleanup after each test. It also stores method name state used to create unique method paths. Cleanup is broad enough that subclasses must override carefully when testing root behavior.

Dependencies and integration points: all abstract contract suites depend on this base for contract flags, filesystem access, path qualification, logging, relaxed exception handling, and common assertions. Concrete Ozone subclasses supply `createContract`.

Risks and test signals: the scheme assertion prevents destructive tests from accidentally targeting local FS. Cleanup failures can contaminate later tests. `handleRelaxedException` enforces strict exception behavior only when `SUPPORTS_STRICT_EXCEPTIONS` is set, so contract flags directly control pass/fail sensitivity.
