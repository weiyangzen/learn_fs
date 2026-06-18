# sources/test-tools/syzkaller/pkg/mgrconfig/load.go

Purpose: Loads, defaults, validates, and completes `mgrconfig.Config` objects, including target resolution, absolute paths, binary locations, service prerequisites, syscall filters, focus areas, and timeouts.

Important APIs and types: `Derived` stores target objects, parsed OS/arch/vmarch, binary paths, enabled syscall ids, no-mutate ids, timeouts, VM-less flag, and modules. Entry points are `LoadData`, `LoadFile`, `LoadPartialData`, `LoadPartialFile`, `DefaultValues`, `SetTargets`, and `Complete`. Helpers include `CompleteKernelDirs`, `KernelDirs`, `checkSSHParams`, `completeBinaries`, `completeFocusAreas`, `SplitTarget`, `ParseEnabledSyscalls`, `ParseNoMutateSyscalls`, and `MatchSyscall`.

Control flow: Partial load applies defaults, parses config with comment-tolerant config loader, and resolves target. `Complete` enforces required fields, absolutizes workdir/image/syzkaller/kernel paths, validates binaries and SSH key permissions, completes service settings, parses description mode, computes enabled syscalls and no-mutate calls, normalizes focus areas and legacy cover filter, initializes target-specific timeouts with slowdown heuristics, and rejects reproduction in VM-less mode.

State and persistence: No persistence; mutates config in memory. `osutil.Abs` enforces stable process working directory. Asset storage validation depends on dashboard configuration.

Dependencies and integration: Depends on syzkaller `prog`, `targets`, config loader, os utilities, and vminfo. Used before manager, repro, HTTP, VM, and report construction.

Risks: `completeServices` error is currently swallowed by `Complete` (`return nil`) if service completion fails, which can hide invalid hub/dashboard/asset config. Path existence checks can make tests/environment setup brittle. Syscall matching patterns are prefix-based and exact-dollar aware; unexpected patterns may enable more calls than intended.

Test signals: `load_test.go` covers description-mode and snapshot filtering. `mgrconfig_test.go` covers canned config loading and syscall pattern matching.
