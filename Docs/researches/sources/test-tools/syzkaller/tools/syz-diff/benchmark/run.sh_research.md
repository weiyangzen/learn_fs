# sources/test-tools/syzkaller/tools/syz-diff/benchmark/run.sh

Purpose: this benchmark driver builds base and patched Linux kernels for known bug-introducing commits and runs `syz-diff` experiments for network and filesystem bug lists.

Important APIs and flow: it requires base repo, patched repo, and image path arguments; computes script/base directories; downloads a kernel config; patches `%KERNEL%`, `%SYZKALLER%`, and `%IMAGE%` placeholders; defines `run_experiment` to reset/build the base kernel with the guilty commit reverted, build the patched kernel at the guilty commit, create a timestamped experiment workdir, save commit metadata and patch, copy/personalize configs, clear patched crashes, run `timeout 3h bin/syz-diff -patch`, tee logs, grep `patched-only`, and copy crashes. It then calls `run_experiment` for hard-coded net and fs commits/titles.

State and persistence: destructive git state changes happen inside both kernel repos (`git clean -fxfd`, `git reset --hard`, `git revert`). Experiment outputs are stored under `experiment/<timestamp>_<commit>/`.

Dependencies and integration: uses `wget`, `git`, `make`, clang/lld, syzkaller `bin/syz-diff`, benchmark configs, QEMU/KVM image, and existing `workdir_net`/`workdir_fs` corpuses per script comment.

Risks: highly destructive to supplied kernel repos; no cleanup of temp kernel config; fixed build parallelism `-j32`; no error checking for failed builds because subshell output is redirected and script lacks `set -e`; grep may affect pipeline status. Requires large disk/time resources.

Test signals: no automated unit test. Evidence is per-experiment log, patch.diff, description, and copied crashes.
