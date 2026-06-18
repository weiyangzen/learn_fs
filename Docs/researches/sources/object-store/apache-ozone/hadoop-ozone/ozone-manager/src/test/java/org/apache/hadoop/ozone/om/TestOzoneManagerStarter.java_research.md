# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerStarter.java

Purpose: Tests the Picocli-backed `OzoneManagerStarter` command dispatch for start, init, upgrade/cancel-prepare, error handling, and usage output.

Important APIs and types: `OzoneManagerStarter`, `OMStarterInterface`, `GenericCli.EXECUTION_ERROR_EXIT_CODE`, Picocli exit codes `OK` and `USAGE`, `OzoneConfiguration`, and `AuthenticationException`.

Control flow: each test captures stdout/stderr, installs a `MockOMStarter`, executes command-line args, and checks the exit code plus method flags. The mock can throw on start/init/upgrade or return false from init. Invalid-option tests assert no action method ran and stderr starts with unknown-option usage text.

State and persistence: no persistent state. It temporarily replaces `System.out` and `System.err` and restores them after each test.

Dependencies and integration points: verifies CLI-to-service dispatch used by OM process startup. Bootstrap is implemented in the mock but not tested here.

Risks and edge cases: invalid options must not call service methods; failed init returning false must map to execution error; upgrade flag should call `startAndCancelPrepare`; stderr encoding must be stable for regex matching.

Test signals: exact exit codes, boolean flags on the mock starter, simulated exception paths, and regex match for usage text on invalid input.
