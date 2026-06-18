# sources/test-tools/syzkaller/pkg/manager/diff/patch.go

Purpose: Converts patch information and symbol-hash differences into manager focus areas so patch fuzzing biases generation toward modified functions, directly changed files, and source files transitively affected by changed headers.

Important APIs: `PatchFocusAreas` mutates `cfg.Experimental.FocusAreas`. `affectedFiles` extracts changed files from git diffs and greps `.c` files including changed headers. `modifiedSymbols` compares base and patched symbol hash maps and returns changed symbol names if the changed-symbol ratio is specific enough.

Control flow: `PatchFocusAreas` first adds a high-weight `symbols` area for modified functions, then a medium-weight `files` area for directly changed patch files, then a lower-weight `included` area for `.c` files including changed headers. If any focus area exists, it appends a final empty-filter area with weight 1.0 so the rest of the kernel remains fuzzable. `affectedFiles` skips transitive header expansion if `KernelSrc` is empty and suppresses very widespread headers after 50 matches. `modifiedSymbols` returns nil once changes exceed 5% of patched symbols.

State and persistence: No persistence; the function mutates in-memory manager config before coverage filter preparation.

Dependencies and integration: Uses `vcs.ParseGitDiff`, `osutil.GrepFiles`, `mgrconfig.FocusArea`, and manager coverage-filter logic later consumed by `kernelContext.CoverageFilter`.

Risks: Header include detection is textual and only looks for `<trimmed-header>`, so quoted includes or generated dependencies can be missed. The 5% symbol threshold avoids overbroad focus but can discard useful symbol focus for medium-sized patches. Direct file names must match coverage report file naming.

Test signals: `patch_test.go` covers modified function focus, direct changed files, header transitive include expansion, fallback area, and symbol threshold behavior.
