# sources/test-tools/syzkaller/tools/syz-diff/benchmark/base.cfg

Purpose: this JSON manager config template defines the baseline VM setup for syz-diff benchmark experiments.

Important fields and flow: placeholders `%KERNEL%`, `%IMAGE%`, and `%SYZKALLER%` are patched by `run.sh`. It names the instance `base`, listens on `0.0.0.0:50543`, targets `linux/amd64`, uses QEMU, three procs, four VMs, `workdir_fs`, KVM-enabled q35 machine args, 2 CPUs, 2048 MB memory, and disables experimental edge coverage.

State and persistence: syz-manager state goes under `%SYZKALLER%/workdir_fs`; this config itself is copied into per-experiment directories.

Dependencies and integration: consumed by benchmark `run.sh` and `bin/syz-diff` as the reverted/base kernel side.

Risks: the workdir is shared with fs experiments, so benchmark scripts remove crash state elsewhere. Placeholder replacement must happen before use. Fixed ports can collide with local managers.

Test signals: no unit test; validation is successful syz-diff launch with patched placeholders.
