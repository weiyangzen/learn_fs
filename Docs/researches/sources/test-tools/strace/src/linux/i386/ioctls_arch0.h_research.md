# sources/test-tools/strace/src/linux/i386/ioctls_arch0.h

Purpose: provides the `i386` generated architecture ioctl table, with 132 initializer rows from asm/amd_hsmp.h, asm/mce.h, asm/msr.h, asm/mtrr.h; examples include HSMP_IOCTL_CMD, MCE_GETCLEAR_FLAGS, MCE_GET_LOG_LEN, MCE_GET_RECORD_LEN, X86_IOC_RDMSR_REGS, X86_IOC_WRMSR_REGS.

Important APIs/types/functions: each row is `{'header, name, direction, number, size'}` data consumed by the common ioctl xlat machinery; observed direction flags include _IOC_NONE, _IOC_READ, _IOC_WRITE.

Control flow: no executable flow; entries are compiled into lookup arrays that let `ioctl(2)` decoding map command numbers back to symbolic names and argument direction/size.

State/persistence behavior: immutable compile-time metadata only; it neither reads traced memory nor persists runtime state.

Dependencies/integration: generated from Linux UAPI headers by `ioctls_gen.sh` and consumed by the strace ioctl decoder alongside generic include tables.

Risks/test signals: stale generated rows or wrong command sizes cause misleading ioctl names or argument decoding; test by comparing generated tables with current UAPI headers and tracing representative architecture-specific ioctl calls.

Source-read signal: reviewed complete local file (133 lines).
