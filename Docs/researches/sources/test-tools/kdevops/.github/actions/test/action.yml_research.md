# sources/test-tools/kdevops/.github/actions/test/action.yml

Purpose: composite GitHub Action that runs a selected kdevops test workflow, classifies results, and generates commit-message metadata for the archive.

Important APIs/types/functions: inputs are `ci_workflow`, `test_mode`, and optional `tests`. Step `ci_test` determines `TESTS`, writes it to GitHub output, records `ci.start_time`, and runs `make ci-test CI_WORKFLOW=...`. Step `setpath` maps workflow names to result paths. The final step reads result files, writes `ci.commit_extra`, sets `ci.result`, exports CI context, and runs `scripts/generate_ci_commit_message.sh` to create `ci.commit_message_enhanced`.

Control flow: if `tests` input is provided, use it; otherwise in `kdevops-ci` mode choose a small representative test by workflow pattern (`generic/003`, `block/003`, or `kmod/test_001`); in `linux-ci` mode leave `TESTS` empty for full suites. After tests run, map workflow to `workflows/blktests`, `workflows/fstests`, or `workflows/selftests`. Result classification is workflow-specific: fstests reads `xunit_results.txt` or dmesg fallback and greps failure/error counts; blktests counts unique result files and `.out.bad`; selftests reads `*.userspace.log` and scans pass/fail strings; default mode tails dmesg/userspace logs and greps for failure.

State/persistence behavior: writes `ci.start_time`, `ci.commit_extra`, `ci.result`, and `ci.commit_message_enhanced`, and reads test results from `workflows/*/results/last-run`. The make target mutates guest and workflow result state.

Dependencies/integration: depends on prior configure/bringup/linux/build-test actions, `scripts/github_output.sh`, kdevops `ci-test` target, workflow result directory conventions, and `scripts/generate_ci_commit_message.sh`.

Risks/test signals: the action uses heuristic grep-based result classification that can misclassify unusual logs. The final step references `inputs.kernel_tree` even though this action does not declare that input, so it falls back to `linux` via expression defaulting; this is intentional-looking but easy to misunderstand. A test signal is correct `ci.result` for known passing/failing fixture result directories and a generated enhanced commit message.
