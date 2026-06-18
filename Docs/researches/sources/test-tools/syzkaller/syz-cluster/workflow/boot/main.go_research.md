## sources/test-tools/syzkaller/syz-cluster/workflow/boot/main.go

`boot-action` runs a smoke boot test for a supplied kernel artifact and reports session-test status. Flags include session ID, test name, base/patched build IDs, output path, and whether to report boot failures as findings.

`main` uploads a running `api.SessionTest`, runs `runTest` with a timestamped tracer whose output becomes the final log, uploads passed/failed status, and optionally writes an `api.BootResult`. `runTest` generates a base fuzz config, forces VM count to three, completes the manager config, and calls `instance.RunSmokeTest` up to three times. Three consecutive reports are required before failure. When `-findings` is true, the final report is uploaded as a raw finding; otherwise report/output are logged.

State persists through controller API calls for session tests and findings. Integration is with Argo boot template, syzkaller instance smoke tests, fuzzconfig generation, and build artifacts mounted at expected paths. Risks include fatal exits leaving only the initial running state, hard-coded workdir, fixed retry policy, and reliance on global flags inside `runTest`. There are no direct tests in this file.
