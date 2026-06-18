# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/server/TestStorageContainerManagerStarter.java

Purpose: This class tests the picocli front end for `StorageContainerManagerStarter` without starting SCM services. It validates that top-level start, initialization, bootstrap, and cluster-id generation options dispatch to `SCMStarterInterface` correctly and produce the expected exit codes.

Important APIs and types: The test uses `StorageContainerManagerStarter.execute`, `SCMStarterInterface`, `GenericCli.EXECUTION_ERROR_EXIT_CODE`, and picocli `ExitCode`. The nested `MockSCMStarter` records calls to `start`, `init`, `bootStrap`, and `generateClusterId`, captures the cluster ID argument, and can throw from each operation.

Control flow: `@BeforeEach` replaces `System.out` and `System.err` with UTF-8 `PrintStream`s backed by byte arrays, then creates a fresh mock starter. Individual tests call `executeCommand` with option combinations such as no args, `--init`, `--bootstrap`, `--clusterid`, `--genclusterid`, and invalid switches. `@AfterEach` restores the original streams.

State and persistence behavior: There is no SCM metadata persistence. The observable state is the mock starter's boolean flags, the saved cluster ID, process-style exit code, and captured stderr usage text for invalid input.

Dependencies and integration points: It covers the CLI binding around SCM startup actions, including usage validation, exception mapping, standard output/error behavior, and the `OzoneConfiguration` parameter contract exposed through `SCMStarterInterface`.

Risks: Because global streams are replaced, failures before `restoreStreams` can contaminate later tests. The mock `initStatus` is always true, so unsuccessful false-return init/bootstrap behavior is not tested. The usage assertion uses a regex tied to picocli's invalid-option wording.

Test signals: Expected signals are OK for start/init/bootstrap/genclusterid, usage exit for invalid parameters with no side-effect call, execution-error exit when mock operations throw, cluster ID propagation for `--init --clusterid=...`, and stderr containing unknown-option usage text.
