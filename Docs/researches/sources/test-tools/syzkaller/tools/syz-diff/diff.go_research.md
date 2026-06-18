# sources/test-tools/syzkaller/tools/syz-diff/diff.go

Purpose: `syz-diff` compares fuzzing behavior between a base and new manager configuration, optionally focusing the new config using a git patch.

Important APIs and flow: `main` requires a build with known git revision, parses `-base`, `-new`, `-debug`, and `-patch`, enables log caching, loads both manager configs, optionally reads a patch and calls `diff.PatchFocusAreas(newCfg, ...)`, then runs `diff.Run` with a `manager.DiffFuzzerStore` rooted at the new config workdir and a shutdown context.

State and persistence: manager/diff state is stored under `newCfg.Workdir` through `DiffFuzzerStore`. Log cache is in memory. VM shutdown is context-driven.

Dependencies and integration: uses `pkg/manager/diff`, `pkg/manager`, `mgrconfig`, `vm`, syzkaller build revision metadata, and optional patch parsing through the diff package.

Risks: missing/invalid configs are fatal. Patch focusing mutates the new config's focus areas and depends on diff package heuristics. It refuses non-`make` builds with unknown git revision.

Test signals: no direct test here; benchmark configs and `run.sh` exercise it. Package-level tests for `manager/diff` would be the primary logic signal.
