# sources/test-tools/syzkaller/tools/syz-diff/benchmark/patched_net.cfg

Purpose: this syz-diff manager config template defines the patched-kernel side for networking-focused benchmark experiments.

Important fields and flow: it enables common socket/syscall operations plus BPF, cgroup, tun/ppp, namespace procfs, 802.11, ethernet, TCP resource extraction, net socket initialization, and VHCI helpers. It uses QEMU with 18 VMs, 4 procs, no sandbox, 3072 MB memory, and disabled edge coverage.

State and persistence: despite being network-focused, `workdir` is `%SYZKALLER%/workdir_fs` in this template. `run.sh` prepares and copies crash artifacts around this workdir.

Dependencies and integration: selected by `run.sh` for network bug commits and passed to `bin/syz-diff` as the new/patched config.

Risks: duplicate `bpf` entry, shared `workdir_fs`, fixed port, host KVM requirements, and manually maintained syscall allowlist. Network fuzzing may need external kernel config support not enforced here.

Test signals: benchmark output filtered for `patched-only` lines indicates useful differential crashes.
