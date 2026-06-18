## sources/test-tools/syzkaller/prog/target_test.go

Purpose: tests glob pattern helper behavior used by target buffer glob values.

Important APIs/types/functions: `TestRequiredGlobs` and `TestPopulateGlob`.

Control flow: tests pass colon-separated include/exclude patterns into `requiredGlobs` and `populateGlob`, then compare sorted results.

State and persistence: no state beyond local maps and slices.

Dependencies/integration: targets with `BufferGlob` types rely on these helpers through `RequiredGlobs` and `UpdateGlobs`.

Risks: pattern strings assume tokens are non-empty because production helpers index `tok[0]`. Exclusions only remove exact file names.

Test signals: focused coverage for include/exclude semantics and deterministic sorted output.
