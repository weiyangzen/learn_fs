# sources/test-tools/syzkaller/tools/syz-testbed/instance.go

## Purpose
This file defines executable testbed instances and the concrete `syz-manager`/`syz-repro` instance setup, execution, stopping, and result extraction logic.

## Important APIs, types, and functions
- `Instance` interface requires `Run`, `Stop`, `FetchResult`, and `Uptime`.
- `InstanceCommon` stores process command, args, log path, start/stop timestamps, and stop channel; its `Run`, `Stop`, and `Uptime` implement shared process lifecycle behavior.
- `SyzManagerInstance` embeds `InstanceCommon`/`SyzkallerInfo`, adds runtime, and fetches bug/bench results.
- `SetupSyzkallerInstance` creates workdir/config/bench paths and patches manager config JSON.
- `SyzManagerTarget.newSyzManagerInstance` creates a configured `syz-manager` run folder and command.
- `SyzReproInstance` and `SyzReproTarget.newSyzReproInstance` copy an execution log and run `syz-repro` with output/title paths.

## Control flow
`InstanceCommon.Run` creates a gracious command, redirects stdout/stderr to a log file if configured, starts the process, and waits for completion or stop signal. Stop sends interrupt, waits up to one minute, then kills. Manager instances wrap common run with a `time.After(RunTime)` timeout. Repro instances run until `syz-repro` exits and derive success from produced files and title matching.

## State and persistence behavior
Each instance creates a `run-<uniq>` folder under a checkout, with workdir, manager config, bench file, log, and repro-specific artifacts. Runtime timestamps are in memory. `FetchResult` reads crash stores, bench files, and output files to produce result structs.

## Dependencies and integration points
Uses `pkg/config` for JSON patching, `pkg/osutil` for process/file helpers, local `collectBugs`/`readBenches`, and built syzkaller binaries in each checkout. It is invoked by target strategies in `targets.go` and slots in `testbed.go`.

## Risks and edge cases
`cmd.Start()` error is ignored before `cmd.Wait`, which can make startup failures less clear. Log files are created but not explicitly closed in `Run`. `SyzReproInstance.FetchResult` treats a different reproduced title as failure, which is correct for benchmarking but can discard evidence of another bug. Manager run timeout uses `time.After`, so very long runtimes allocate a timer per instance.

## Test signals
No direct tests. Good tests would fake commands to cover graceful stop, kill-after-timeout, log creation failures, title mismatch, and generated manager/repro config paths.
