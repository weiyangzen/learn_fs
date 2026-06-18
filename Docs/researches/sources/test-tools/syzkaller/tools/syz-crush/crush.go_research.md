# sources/test-tools/syzkaller/tools/syz-crush/crush.go

Purpose: `syz-crush` repeatedly replays a syzkaller execution log or C reproducer across all VMs in a manager config to amplify elusive crash reproduction. It accepts `-config`, `-debug`, `-restart_time`, `-infinite`, and `-strace`, builds a VM pool, creates a report parser, and uses the reproducer basename as the manager tag when no tag is configured.

Important APIs and flow: `main` validates flags, loads `mgrconfig.Config`, creates `vm.Pool` and `report.Reporter`, chooses `LogFile` versus `CProg` from the input suffix, and starts one goroutine per VM. Each worker loops through `runInstance`, sends a `*instance.RunResult` on `runDone`, and stops on interrupt or non-infinite mode. `runInstance` creates an execprog-backed VM instance, runs either `RunSyzProgFile` with `csource.DefaultOpts` (`Repeat` and `Threaded` enabled) or `RunCProgRaw` with raw C source, and returns only when a parsed crash report is present. `storeCrash` hashes the report title, allocates a sequential crash index, and writes description, log, tag, report, reproducer, and optional memory dump.

State and persistence: runtime state is mostly channels and atomics (`shutdown`, `stoppedWorkers`). Persistent output is stored beside the reproducer under `crashes/<hash(title)>/`, with append-only `logN`, `tagN`, `reportN`, `reproducerN`, and `memory_dumpN` files. Temporary memory dumps are removed when no crash is kept.

Dependencies and integration: this command depends on syzkaller manager config, VM backends, `pkg/instance`, crash reporting, C-source options, and `osutil.HandleInterrupts`. It integrates directly with VM shutdown through global `vm.Shutdown`.

Risks: a missing `strace_bin` is fatal when `-strace` is set; C source read errors call `log.Fatalf` inside workers; crash directory indexing is not synchronized across processes; infinite mode runs until signal and can accumulate crash artifacts indefinitely. Non-crash execution errors are logged and treated as no result.

Test signals: no local unit test is assigned. Behavior is indirectly covered by VM/instance/report package tests and by integration use of crash artifact layout.
