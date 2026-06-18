# sources/sync-backup/rsync/.github/workflows/scan-build.yml

Purpose: run clang static analyzer and publish findings without gating merges.

Important APIs/types/functions: installs clang/clang-tools and dependencies, runs `scan-build ./configure`, then `scan-build -o scan-report make check-progs`, writes analyzer bug count to the GitHub step summary, and uploads the HTML report.

Control flow: push/PR path-filtered and manual triggers. It deliberately omits `--status-bugs`, so analyzer reports do not fail the job.

State and persistence: `scan-build-report` artifact, ignored if no files.

Dependencies/integration: integrates clang analyzer with configure-generated compiler wrappers.

Risks: informational status can allow real analyzer findings to be ignored; false positives are expected and documented.

Test signals: artifact and summary show static-analysis deltas; build of `check-progs` ensures analyzer sees main/test-helper code.
