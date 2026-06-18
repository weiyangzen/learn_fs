## sources/test-tools/syzkaller/pkg/instance/dump.go

Purpose: extracts Linux crash memory dumps from a VM after panic through `makedumpfile`.

Important APIs/types/functions: `ExtractMemoryDump` and `extractKdumpInner`.

Control flow: validates Linux target, retries up to 100 times with 3-second sleeps, logs each failed attempt, and streams `makedumpfile -F -c -d 0 /proc/vmcore` stdout into the requested host file with a one-hour timeout.

State and persistence: writes the dump to the caller-provided path. No package state.

Dependencies and integration: uses `runStreamAndCollectStdout` from `execprog.go`, `vm.Instance`, target metadata, and syzkaller logging.

Risks: retry loop can take about five minutes before failing. Partial dump files may remain on failure from `extractKdumpInner`. Command assumes crash-kernel environment and Linux `makedumpfile`.

Test signals: stream helper is unit-tested in `execprog_test.go`; dump extraction itself is integration-heavy and not directly tested here.
