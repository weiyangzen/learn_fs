<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/arch_kvm.c -->
# sources/test-tools/strace/src/linux/x86_64/arch_kvm.c

Purpose: architecture-specific KVM ioctl printers for x86 general and special registers.
Important APIs/types/functions: `arch_print_kvm_regs`, `arch_print_kvm_sregs`, segment/dtable helpers, `struct kvm_regs`, `struct kvm_sregs`, and `PRINT_FIELD_*` macros.
Control flow: compiled only when kernel headers expose the relevant KVM structs. Register printers emit a shortened view in abbreviated mode and full segment/control-register state otherwise.
State and persistence behavior: stateless formatting of ioctl buffers. Dependencies and integration points: included by generic KVM ioctl decoder.
Risks: kernel header feature guards and abbreviated branches can miss fields after structure growth. Test signals: KVM_GET_REGS/SREGS ioctl fixtures in abbreviated and verbose modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/arch_kvm.c -->
