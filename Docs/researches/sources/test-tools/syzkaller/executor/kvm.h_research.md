# sources/test-tools/syzkaller/executor/kvm.h

Purpose: Shared KVM/SYZOS constant header defining guest memory layouts, architecture control bits, selectors, MSRs, VMCS/VMCB fields, and generic KVM sizing constants.

Important content: on amd64 it defines legacy x86 setup addresses, SYZOS memory map regions, per-L1-VCPU and per-L2-VM layout macros, segment selectors, CR0/CR4/EFER bits, page-table bits, EPT flags, selector indexes, MSR numbers, VMX/SVM access-rights constants, VMCS fields, VMCB offsets, and magic placeholders `X86_NEXT_INSN`/`X86_PREFIX_SIZE`. Generic constants include `KVM_MAX_VCPU`, `KVM_MAX_L2_VMS`, `KVM_PAGE_SIZE`, `KVM_GUEST_PAGES`, and `GENMASK_ULL`. Arm64 and riscv64 sections define interrupt-controller, exit, dirty-page, user-code, executor-code, scratch, stack, and table addresses.

State and dependencies: no runtime state; it is a compile-time contract shared by assembly, generated blobs, KVM pseudo-syscalls, and tests.

Integration points: included by `kvm_amd64.S`, `kvm_ppc64le.S`, generated KVM setup code, and Linux KVM tests. Constants must match guest memory initialization in common Linux KVM helpers outside this subset.

Risks and tests: address overlap or stale VMCS/VMCB fields can silently break guest setup. Architecture-specific sections are macro-guarded, so cross-arch compile coverage is important. `test_kvm` and `test_syzos` are the strongest signals.
