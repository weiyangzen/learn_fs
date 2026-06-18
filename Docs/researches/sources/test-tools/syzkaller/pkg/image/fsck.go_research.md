## sources/test-tools/syzkaller/pkg/image/fsck.go

Purpose: runs an external fsck command against an image stream and caches fsck binary availability.

Important APIs/types/functions: `Fsck(r, fsckCmd)` and `FsckChecker.Exists`.

Control flow: `Fsck` writes the reader to a temporary image, closes it, adjusts sandbox ownership, builds the command from `strings.Fields(fsckCmd)` plus the temp path, sandboxes the command, runs it, captures combined output, and reports clean status from exit code zero. `FsckChecker.Exists` caches `exec.LookPath` results by command binary.

State and persistence: creates and removes a temporary `*.img`; `FsckChecker` keeps an in-memory mutex-protected existence map.

Dependencies and integration: depends on `osutil.SandboxChown`, `osutil.Sandbox`, external fsck tools, and syzkaller logging for missing binaries.

Risks: `strings.Fields(fsckCmd)[0]` panics for empty command. Shell quoting is not supported because fields are split naively. External command behavior and sandbox permissions drive correctness.

Test signals: `fsck_test.go` covers success/corruption behavior when required fsck tools exist.
