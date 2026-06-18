# sources/test-tools/stress-ng/stress-sigsegv.c

Purpose: implements the `sigsegv` stressor, generating recoverable segmentation-related faults from protected mappings, random invalid addresses, guard pages, VDSO bad pointers, and selected x86 privileged or malformed instruction cases.

Important APIs/types/functions: `stress_segvhandler`, `stress_sigsegv`, x86 helpers such as `stress_sigsegv_x86_trap`, `stress_sigsegv_x86_int88`, `stress_sigsegv_rdmsr`, `stress_sigsegv_misaligned128nt`, `stress_sigsegv_readtsc`, `stress_sigsegv_read_io`, optional `stress_sigsegv_vdso`, `mmap`, `madvise(MADV_GUARD_INSTALL)`, `sigaction`, `sigsetjmp`, `prctl(PR_SET_TSC)`, `stress_put_uint8`, and siginfo fields.

Control flow: the worker maps a read-only page and a PROT_NONE page, optionally installs a guard page, synchronizes start, and repeatedly installs SIGSEGV/SIGILL/SIGBUS handlers before setting a jump point. On the non-fault path it randomly chooses one of several fault generators: overlong x86 instruction trap, illegal interrupt, privileged MSR read, misaligned non-temporal store, disabled TSC read, I/O port read, VDSO call with bad pointer, write to read-only memory, read from PROT_NONE, guard-page access, or random masked-address read. On the signal-return path it optionally verifies expected fault address and signal/code before incrementing bogo ops.

State and persistence behavior: state is anonymous mappings plus global signal metadata and address-mask progression used to walk through invalid address widths. TSC reads are re-enabled on exit if disabled. No durable files are created.

Dependencies and integration points: registered as `CLASS_SIGNAL | CLASS_OS`, optional verify with `SA_SIGINFO`, and unimplemented without siglongjmp. It depends heavily on architecture, Linux feature guards, CPU capability helpers, cache flush helpers, and mmap/madvise availability.

Risks and test signals: fault type and `si_addr` fidelity vary widely by architecture and kernel. Real failures are inability to recover from a fault, wrong unexpected signal in verify mode, address mismatch outside tolerated ranges, leaked mappings, or failing to restore PR_SET_TSC state.
