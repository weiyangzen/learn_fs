# sources/test-tools/syzkaller/tools/syz-fix-analyzer/fix-analyzer.go

Purpose: `syz-fix-analyzer` estimates how many fixed dashboard bugs look automatically fixable based on bug type and patch shape.

Important APIs and flow: `main` compiles regexes for bug types, creates a dashboard API client, calls `run`, prints fixable bugs by type, and summarizes totals. `run` opens a Linux repo, fetches fixed bug groups, starts `runJobs`, de-duplicates by first fix commit hash, classifies jobs by regex, and accumulates type stats. `runJobs` uses `runtime.GOMAXPROCS` workers. `isFixable` requires a fix commit, matching bug type, fetches the commit patch, parses it with `git-diff-parser`, and declares the bug fixable only when the patch changes exactly one non-binary `.c` or `.h` file with one hunk and no rename.

State and persistence: no local writes. It reads the git repository, dashboard data, and commit patches; results are printed to stdout.

Dependencies and integration: uses `dashboard/api`, `pkg/vcs`, Linux target repo handling, regex classification, and an external git diff parser.

Risks: fixability heuristic is intentionally shallow; TODOs mention matching guilty files and more crash variants. `percent` divides by total and can print NaN when denominator is zero. `runJobs` never closes `jobC`, but all submitted jobs are consumed before returning.

Test signals: no direct tests. Useful future tests would cover regex classification, patch-shape filtering, duplicate commit handling, and zero denominators.
