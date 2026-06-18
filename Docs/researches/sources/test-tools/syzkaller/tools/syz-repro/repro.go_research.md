# sources/test-tools/syzkaller/tools/syz-repro/repro.go

## Purpose
`syz-repro` runs syzkaller's reproduction pipeline against an execution log using a manager configuration and VM pool, writing found syz/C reproducers and optional title/strace artifacts.

## Important APIs, types, and functions
- Flags configure manager config, VM count override, debug VM output, syz repro path, C repro path, title path, and strace output path.
- `main` loads config/log data, creates VM pool and reporter, reserves dispatcher instances, runs `repro.Run`, prints timings and results, writes outputs, optionally runs strace, and drives `pool.Loop`.
- `recordTitle`, `recordCRepro`, and `recordStraceResult` persist specific result artifacts.

## Control flow
The tool prepends `-vv=10` to args before flag parsing for verbose logging. Reproduction runs in a goroutine with a cancelable context; the VM dispatcher loop runs on the main goroutine until the reproduction completes and cancels context. If a result exists, the serialized syz program is printed and written. C generation uses `csource.Write` and formatting. Strace mode invokes `repro.RunStrace` on the resulting repro.

## State and persistence behavior
Reads manager config and execution log. Uses external VMs through `vm.Create`/dispatcher. Writes repro program, C repro, title, and strace output files depending on flags and result. Handles interrupts by shutting down VM infrastructure.

## Dependencies and integration points
Integrates `pkg/repro`, `pkg/report`, `pkg/mgrconfig`, `pkg/flatrpc` feature flags, `pkg/csource`, `vm` pools, and `pkg/osutil`. Used both standalone and by `syz-testbed` repro benchmarking.

## Risks and edge cases
The default output files in the current directory may be overwritten. The strace result success message says "C file saved" even for strace output. A nil result silently produces no artifact beyond failure logs. VM count override can exceed practical host capacity if misused. The dispatcher/cancel flow relies on `repro.Run` returning and deferring `done()`.

## Test signals
No direct tests in this file. Most logic depends on integration tests around `pkg/repro` and VM backends. Wrapper tests can cover argument validation and artifact writers with fake results.
