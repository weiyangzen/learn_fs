<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/kernel_version.c -->
# sources/test-tools/strace/tests/kernel_version.c

Purpose: Tests strace's `KERNEL_VERSION(a,b,c)` formatting by using BPF syscall attributes that carry kernel-version fields.

Important APIs/types/functions: Uses `syscall(__NR_bpf)`, `union bpf_attr`, `print_bpf_attr`, `bpf_commands` xlat, `PRINT_FIELD_U`, and `sprintrc`.

Control flow: Fills a BPF program-load attribute with deterministic values, varies the command and kernel version fields, invokes the syscall, and prints expected decoded BPF attributes including kernel version representation.

State/persistence behavior: Syscalls are expected to fail; no BPF programs persist. State is the local `bpf_attr` buffer and global `errstr`.

Dependencies: Requires `__NR_bpf`, strace BPF attribute compatibility headers, and xlat mode wrappers.

Integration points: Exercises generic kernel-version pretty-printer through a real syscall decoder path.

Risks: BPF UAPI field layout and validation can change, though failed-call formatting should remain stable.

Test signals: Lines show BPF command xlat, decoded `kern_version=KERNEL_VERSION(...)` or raw variants, errors, and final exit.

Source read signal: complete file read for this research pass; file size 115 line(s), 2289 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/kernel_version.c -->
