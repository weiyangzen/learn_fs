# sources/test-tools/syzkaller/dashboard/config/linux/bits/base.yml

Purpose: foundational Linux kernel config fragment required by syzbot across most kernels. It enables debugging, coverage, namespace/sandbox support, deterministic boot behavior, text/debug metadata, and disables unsafe or noisy facilities.

Important keys: top-level `verbatim` preserves special debug symbols. `config` enables `EXPERT`, `DEBUG_KERNEL`, namespaces, cgroups, KALLSYMS, debug checks, KCOV/KCOV comparisons, debugfs, fault injection, root filesystem/boot support, ext4, and selected platform/network basics. It disables `WERROR`, tracing slowdown features, CPU mitigations, dangerous `/dev/mem` style devices, Magic SysRq, KGDB, Hyper-V/Xen, legacy USB gadget drivers, samples, and Rust by default.

Control flow: declarative fragment with many version/arch/tag conditions (`v6.1`, `-arm`, `-s390`, `-kmsan`, `clang`, `x86_64`, etc.). The config generator merges this with arch/product fragments and applies `CMDLINE` values.

State and persistence: produces generated `.config` and kernel command line. It is central to persistence of syzbot's fuzzing assumptions because many managers inherit it.

Dependencies and integration points: Linux Kconfig across many versions, syzkaller executor sandbox requirements, KCOV coverage, crash parser expectations, qemu boot images, and feature-tag semantics in dashboard config generation.

Risks: this file has high blast radius. Disabling mitigations/tracing improves fuzzing speed but changes production-like behavior. Enabling fault injection and debug checks increases bug-finding but can add noise. Version guards must track symbol renames/removals; wrong guards can break builds. The long `CMDLINE` includes many runtime knobs, so appending incompatible args can break boot.

Test signals: every generated syzbot Linux config effectively validates this file through build, boot, executor sandbox setup, KCOV availability, and crash report quality.
