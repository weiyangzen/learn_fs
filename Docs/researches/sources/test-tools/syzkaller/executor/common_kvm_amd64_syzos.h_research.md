# sources/test-tools/syzkaller/executor/common_kvm_amd64_syzos.h

## Purpose

`common_kvm_amd64_syzos.h` implements the x86-64 SYZOS guest runtime that runs inside a KVM VM. It decodes fuzzer-authored guest commands, executes raw instruction blobs, performs privileged x86 operations, installs simple interrupt handlers, and exposes a nested-virtualization test surface for both Intel VMX and AMD SVM. The file is intentionally self-contained so syzkaller can embed it into executor and csource reproducers.

## Important APIs, Types, and Functions

The `syzos_api_id` enum defines the guest command ABI and must match `sys/linux/dev_kvm_amd64.txt`. Command payloads include `api_call_uexit`, `api_call_code`, `api_call_cpuid`, `api_call_nested_load_code`, and `api_call_nested_load_syzos`. `guest_main()` is the top-level command dispatcher. Basic handlers include `guest_uexit`, `guest_execute_code`, `guest_handle_cpuid`, `guest_handle_wrmsr`, `guest_handle_rdmsr`, `guest_handle_wr_crn`, `guest_handle_wr_drn`, `guest_handle_in_dx`, `guest_handle_out_dx`, and `guest_handle_set_irq_handler`.

Nested state is described by `l2_guest_regs`, `mem_region`, `syzos_boot_args`, and `syzos_globals`. VMX helpers include `nested_enable_vmx_intel`, `nested_vmptrld`, `vmread`, `vmwrite`, `init_vmcs_control_fields`, `init_vmcs_host_state`, `init_vmcs_guest_state`, `nested_create_vm_intel`, and `guest_handle_nested_vmentry_intel`. SVM helpers include `nested_enable_svm_amd`, VMCB read/write helpers, `init_vmcb_guest_state`, `nested_create_vm_amd`, and `guest_run_amd_vm`. Cross-vendor nested handlers normalize exits through `map_intel_exit_reason`, `map_amd_exit_reason`, `guest_uexit_l2`, `nested_vm_exit_handler_intel`, and `nested_vm_exit_handler_amd`.

## Control Flow

`guest_main(cpu)` reads per-vCPU text size from `X86_SYZOS_ADDR_GLOBALS`, walks the command stream at `X86_SYZOS_ADDR_USER_CODE + cpu * KVM_PAGE_SIZE`, validates each command size and API id, and dispatches through an if/else chain instead of a switch to avoid compiler-emitted jump tables. Normal completion calls `guest_uexit(UEXIT_END)`; malformed command streams call `UEXIT_INVALID_MAIN`.

Basic command handlers execute inline assembly directly: CPUID, MSR reads/writes, CR/DR writes, I/O port reads/writes, raw code calls, and IDT entry replacement. Nested setup first enables VMX or SVM according to `get_cpu_vendor()`, then creates a per-CPU/per-L2-VM control block, page table root, and code/stack backing. `setup_l2_page_tables()` mirrors the L1 boot memory layout into EPT/NPT mappings while leaving `NO_HOST_MEM` regions unmapped so L2 writes to the uexit page become nested page faults.

Intel vmentry loads the active VMCS, records `active_vm_id`, updates `VMCS_HOST_RSP`, restores persisted L2 GPRs from `syzos_globals`, and executes `vmlaunch` or `vmresume`. The VM-exit assembly shim saves L2 registers, reads `VMCS_VM_EXIT_REASON`, calls `nested_vm_exit_handler_intel`, unwinds back to the L1 command loop, and reports VM-entry failures through a synthetic uexit. AMD vmentry similarly prepares host stack context, syncs RAX into the VMCB, executes `vmrun`, saves VMCB/GPR state on return, calls `nested_vm_exit_handler_amd`, restores L1 state, and re-enables GIF with `stgi`.

Nested exit handlers persist L2 registers, detect EPT/NPT faults on `X86_SYZOS_ADDR_EXIT`, map those into nested uexit codes by incrementing the high-byte nesting level, and otherwise report normalized HLT, INVD, CPUID, RDTSC, RDTSCP, and page-fault exits. Vendor-specific mutator APIs let the fuzzer mask-write VMCS fields or VMCB offsets, inject AMD events, edit AMD intercept fields, and run SVM `invlpga`, `stgi`, `clgi`, `vmload`, and `vmsave`.

## State and Persistence Behavior

State is stored in guest physical memory, not process globals. `syzos_globals` at `X86_SYZOS_ADDR_GLOBALS` persists per-vCPU text sizes, a non-reclaiming bump allocator over the unused-memory region, L2 register snapshots indexed by `[cpu][vm_id]`, and the active nested VM id per CPU. VMCS/VMCB pages, per-VM code buffers, stacks, MSR bitmaps, architecture-specific VMXON/HSAVE pages, and nested page tables are all addressed by macros from `kvm.h`. The allocator lazily initializes its total size from boot args and uses atomic fetch-add, so allocations persist for the lifetime of the guest and are never freed.

## Dependencies and Integration Points

The header depends on `common_kvm_syzos.h` for `GUEST_CODE`, no-inline attributes, and shared API-call structs, and on `kvm.h` for x86 SYZOS addresses, selectors, VMCS/VMCB constants, EPT/NPT bits, MSR ids, and limits such as `KVM_MAX_VCPU` and `KVM_MAX_L2_VMS`. The host-side x86 KVM setup must map the guest code section, boot args, globals, IDT/GDT/TSS, uexit page, user code, nested VM buffers, and unused heap at the exact addresses expected here. The command ids are coupled to syzkaller descriptions in `dev_kvm_amd64.txt`.

## Risks and Edge Cases

This file is intentionally executing privileged instructions and corruptible guest-provided data, so most failures are expected to manifest as KVM exits, uexits, or guest faults. The command ABI is fragile: changing enum values breaks existing reproducers. Jump tables, global data references, or compiler-generated helper calls are dangerous because SYZOS guest code is copied without normal relocations. Nested virtualization is especially sensitive to stack layout comments matching the assembly save/restore order, VMCS/VMCB offset correctness, and vendor detection. `guest_handle_nested_load_syzos()` seeds L2 globals for all vCPUs but reuses the L1 `globals->l2_ctx` storage for register defaults, so index and VM id bounds rely on the surrounding syscall descriptions. Mask writes to arbitrary VMCS/VMCB fields can create invalid control state by design, but wrapper failures should still produce deterministic uexit codes rather than corrupting L1 execution.

## Test Signals

Useful signals include executor/csource builds for amd64 with both GCC and Clang, style tests that catch forbidden switch/jump-table forms, and KVM smoke programs that exercise each command id. Runtime tests should cover CPUID/MSR/CR/DR/I/O exits, IDT handler installation, `UEXIT_INVALID_MAIN` on malformed command sizes, Intel VMX enable/create/load/vmlaunch/vmresume, AMD SVM enable/create/load/vmrun, nested uexit propagation from L2, normalized exit reason reporting, VM-entry failure reporting, VMCB/VMCS mask mutation, AMD intercept/event injection, and allocator exhaustion in the unused-memory region.
