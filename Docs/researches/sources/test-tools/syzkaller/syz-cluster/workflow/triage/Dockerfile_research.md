## sources/test-tools/syzkaller/syz-cluster/workflow/triage/Dockerfile

This Dockerfile packages `triage-action`. It uses Ubuntu with `git`, creates a fixed UID `syzkaller` user, configures `/workdir` and `/kernel-repo` as safe git directories, copies the action binary, and sets it as entrypoint.

Integration is with triage workflow template, which clones from a kernel repository PVC into `/workdir`. Risks include root/default user interaction despite creating the user, git safe-directory broadening, and package variability from `ubuntu:latest`.
