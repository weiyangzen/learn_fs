<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/filter_seccomp-flag.c -->
# sources/test-tools/strace/tests/filter_seccomp-flag.c

## Purpose
Covers that syscall numbers do not conflict with seccomp filter flags. Source comments describe: Check that syscall numbers do not conflict with seccomp filter flags. PERSONALITY*_AUDIT_ARCH definitions depend on AUDIT_ARCH_* constants. Define these shorthand notations to simplify the syscallent files. Source read: 83 lines, 1868 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "arch_defs.h", "sysent.h", "scno.h", <linux/audit.h>, "xlat/elf_em.h", "xlat/audit_arch.h", "sysent_shorthand_defs.h", "syscallent.h", "syscallent1.h", "syscallent2.h"; defines: XLAT_MACROS_ONLY; C functions: main; struct types: audit_arch_t.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. nested loops cover flag, pointer, size, fd, and translation-mode combinations.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, Linux UAPI headers. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: seccomp-BPF availability and filter installation can vary by kernel/configuration. Test signals: successful compilation and harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/filter_seccomp-flag.c -->
