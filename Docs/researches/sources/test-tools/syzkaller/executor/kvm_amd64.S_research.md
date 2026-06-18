# sources/test-tools/syzkaller/executor/kvm_amd64.S

Purpose: x86 assembly snippets converted into byte arrays for KVM guest setup and mode-transition prefixes.

Important APIs and control flow: exported symbol pairs include `kvm_asm64_enable_long`, `kvm_asm32_paged`, `kvm_asm32_vm86`, `kvm_asm32_paged_vm86`, `kvm_asm16_cpl3`, `kvm_asm64_cpl3`, `kvm_asm64_init_vm`, and `kvm_asm64_vm_exit`, each with `_end` markers for `kvm_gen.cc`. Snippets enable paging/long mode, load TSS, transition to CPL3 through crafted far returns, enter VM86, initialize VMXON/VMCS state, write host/guest VMCS fields, launch a nested VM, and capture VM-exit diagnostics.

State and dependencies: uses constants from `kvm.h` as absolute guest physical/virtual addresses. The assembly assumes the KVM setup code has prepared GDT, IDT, page tables, VMXON/VMCS memory, TSS, and user code at matching addresses.

Integration points: `gen_linux_amd64.go` and `kvm_gen.cc` convert symbols to `kvm_amd64.S.h`; KVM setup code injects those byte strings into guest memory; `test_linux.h` validates mode combinations.

Risks and tests: VMX control setup is sensitive to CPU MSR allowed bits and selector/access-rights constants. Hardcoded absolute addresses must remain synchronized with `kvm.h`. Test signal is Linux amd64 `test_kvm`, gated by `/dev/kvm`, permissions, CPU VMX support, and kernel version for SMM.
