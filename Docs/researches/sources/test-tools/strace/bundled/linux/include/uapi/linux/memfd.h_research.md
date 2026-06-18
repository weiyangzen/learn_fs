# sources/test-tools/strace/bundled/linux/include/uapi/linux/memfd.h

Purpose: declares flags for `memfd_create(2)`, including close-on-exec, sealing, hugetlb-backed files, executable/no-exec policy, and hugepage size encodings.

Important APIs/types/functions: exports `MFD_CLOEXEC`, `MFD_ALLOW_SEALING`, `MFD_HUGETLB`, `MFD_NOEXEC_SEAL`, `MFD_EXEC`, `MFD_HUGE_SHIFT`, `MFD_HUGE_MASK`, and named hugepage encodings from 64 KiB through 16 GiB.

Control flow: userspace calls `memfd_create(name, flags)`, optionally ORing hugepage size encodings when `MFD_HUGETLB` is set. The returned anonymous file descriptor can later be sealed, mapped, executed, or shared according to flags and kernel policy.

State/persistence behavior: creates an in-kernel anonymous file object whose lifetime follows fd references. Sealing and executable mode affect later writes, mappings, and exec behavior.

Dependencies/integration: depends on `asm-generic/hugetlb_encode.h`. Integrates with `fcntl` seals, `mmap`, tmpfs/hugetlbfs, exec policy, and sandboxing.

Risks and test signals: flag interactions depend on kernel config and sysctls. Tests should decode hugepage encodings, mutually meaningful exec/noexec flags, sealing flag behavior, and unsupported hugepage-size error paths.
