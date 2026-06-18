# sources/test-tools/syzkaller/tools/syz-diff/benchmark/patched_fs.cfg

Purpose: this syz-diff manager config template defines the patched-kernel side for filesystem-focused benchmark experiments.

Important fields and flow: it targets Linux/AMD64 QEMU, uses `%KERNEL%`, `%IMAGE%`, and `%SYZKALLER%` placeholders, names the manager `patched`, listens on port 50544, enables a broad filesystem syscall set plus filesystem ioctls, disables some risky mount image families, sets `procs` to 3, `fuzzing_vms` to 10, and runs 18 VMs with 3072 MB memory.

State and persistence: uses `%SYZKALLER%/workdir_fs`, and `run.sh` removes its `crashes` directory before each experiment and later copies crashes into the experiment workdir.

Dependencies and integration: paired with `base.cfg` and selected by `run.sh` for filesystem bug commits.

Risks: shared workdir and fixed HTTP port can conflict. The syscall allowlist is manually curated and may age as syscall descriptions change. KVM/q35 assumptions are host-dependent.

Test signals: benchmark success is based on syz-diff producing patched-only crashes in the experiment log.
