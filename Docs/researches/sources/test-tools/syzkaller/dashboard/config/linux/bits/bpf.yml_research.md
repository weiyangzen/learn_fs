# sources/test-tools/syzkaller/dashboard/config/linux/bits/bpf.yml

Purpose: enables BPF syscall and optional JIT/preload coverage for BPF-focused syzbot managers.

Important keys: `BPF_SYSCALL`, tag-gated `BPF_JIT` and `BPF_JIT_ALWAYS_ON`, snapshot-gated `BPF_STREAM_PARSER`, and x86_64 v5.10-gated `BPF_PRELOAD`/`BPF_PRELOAD_UMD`.

Control flow: declarative Kconfig fragment with feature and arch/version tags.

State and persistence: changes generated `.config` for BPF managers.

Dependencies and integration points: Linux BPF Kconfig, syzkaller BPF programs, manager tags such as `bpfjit` and `snapshot`, and host/cross build dependencies for BPF preload.

Risks: BPF JIT changes execution and bug surface compared with interpreter mode, so it is tag-limited. BPF preload cross-build dependencies are known fragile and intentionally limited to x86_64.

Test signals: BPF-enabled kernels should build and expose BPF syscall/JIT paths as expected for selected managers.
