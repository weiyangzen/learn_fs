<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/kopiarunner/setpdeath_linux.go -->
# sources/sync-backup/kopia/tests/tools/kopiarunner/setpdeath_linux.go

This Linux implementation configures async Kopia commands with `syscall.SysProcAttr{Pdeathsig: SIGTERM}`. It returns nil unchanged when given nil.

The behavior ensures server processes launched by `Runner.RunAsync` are signaled if the parent test process dies, reducing leaked Kopia servers during robustness failures.

State is process attribute mutation before start. Risks include relying on Linux-specific semantics, existing `SysProcAttr` fields being overwritten if future code sets them earlier, and SIGTERM not guaranteeing cleanup. Integration is with server-mode snapshotters and multiclient tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/kopiarunner/setpdeath_linux.go -->
