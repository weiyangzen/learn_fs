# sources/security-integrity/cryfs/old-cpp/test/cryfs-cli/testutils/CliTest.h

Purpose: This header defines `CliTest`, a rich Google Test fixture for end-to-end CryFS CLI tests. It provides temporary basedir/mountdir/config paths, fake home-directory behavior, mock console state, fake HTTP version-checking, mount/unmount helpers, and process-level execution helpers.

Important APIs/types/functions: It includes `cryfs-cli/Cli.h`, `VersionChecker`, `FakeHttpClient`, subprocess and tempfile utilities, Dokan/FUSE unmount support, and `TestWithFakeHomeDirectory`. Important methods include `run`, `run_filesystem`, `EXPECT_EXIT_WITH_HELP_MESSAGE`, `_unmount`, `_exit`, `_createDir`, and `_testFs`.

Control flow: A test constructs the fixture, invokes `run` with CLI arguments, and the helper drives `Cli` while collecting exit code, stdout/stderr, logging, mount lifecycle, and fake network responses. Filesystem-oriented tests can call `run_filesystem` to start a mounted filesystem and synchronize startup with condition barriers.

State and persistence behavior: The fixture owns temp directories/files for basedir, mountdir, config, local state, and mount lifecycle. It also mutates fake home-directory state and can launch subprocess/unmount activity, so cleanup and teardown ordering matter.

Dependencies and integration points: This is the main integration harness for CryFS CLI, console I/O, version checking, local state, mount setup, and platform-specific unmount behavior.

Risks: CLI tests using this fixture can be timing-sensitive around mount startup and unmount. Platform differences between Dokan and FUSE, process exit handling, and fake HTTP state can affect determinism.

Test signals: Expected exit codes, help text, mounted filesystem availability, unmount completion, fake HTTP calls, and temp path side effects are the observable signals.
