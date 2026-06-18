# sources/user-network-fs/gcsfuse/tools/integration_tests/util/mounting/mounting.go

Purpose: central low-level helper for invoking a gcsfuse or mount.gcsfuse binary from integration-test mounting packages.

Important APIs/types/functions: `MountGcsfuse(binaryFile string, flags []string) error`.

Control flow: constructs `exec.Command(binaryFile, flags...)`, ensures the integration log directory exists, appends the command line to `setup.LogFile()`, runs the mount command via `CombinedOutput`, and wraps any mount failure.

State/persistence behavior: writes the command invocation to the configured log file and creates its parent directory. The actual mount is external process state controlled by gcsfuse/fusermount.

Dependencies/integration: used by static, dynamic, only-dir, and persistent mounting helpers. It depends on `setup.LogFile()` and `operations.CloseFile`.

Risks/test signals: if opening the log file fails, the code still defers `operations.CloseFile(file)` on a possibly nil file, which can panic. Errors are surfaced primarily through mount command output and wrapped process failures.
