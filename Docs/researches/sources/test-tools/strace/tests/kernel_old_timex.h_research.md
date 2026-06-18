<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/kernel_old_timex.h -->
# sources/test-tools/strace/tests/kernel_old_timex.h

Purpose: Compatibility header defining the old Linux kernel `timex`-related layout needed by strace tests for legacy time adjustment ABIs.

Important APIs/types/functions: Provides header-only type definitions for old-kernel time fields. It exports no runtime functions.

Control flow: No runtime control flow; including tests instantiate the compatibility structure and pass it to syscall decoders.

State/persistence behavior: No persistent or runtime state. The header controls compile-time data layout only.

Dependencies: Depends on strace's kernel compatibility type strategy and consumers that require old time ABI layouts instead of host libc definitions.

Integration points: Supports time/timex syscall tests where decoder correctness depends on exact old-kernel field order and widths.

Risks: Any mismatch with the kernel ABI produces false confidence in decoder tests. Host header substitution would make cross-architecture output unstable.

Test signals: Dependent tests compile and print old-timex fields consistently.

Source read signal: complete file read for this research pass; file size 25 line(s), 530 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/kernel_old_timex.h -->
