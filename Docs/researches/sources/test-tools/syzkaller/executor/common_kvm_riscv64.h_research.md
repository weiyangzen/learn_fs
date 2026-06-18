# sources/test-tools/syzkaller/executor/common_kvm_riscv64.h

## Purpose

`common_kvm_riscv64.h` is the host-side RISC-V 64-bit KVM setup layer for syzkaller. It provides the legacy `syz_kvm_setup_cpu` path for one vCPU, the SYZOS VM/multi-vCPU path, guest memory registration, register initialization, assertion helpers, and guest code validation/installation for RISC-V SYZOS.

## Important APIs, Types, and Functions

The file defines KVM register id helpers `RISCV_CORE_REG` and `RISCV_CSR_REG`, enum indices for KVM core and CSR registers, SSTATUS bits, `kvm_set_reg`, and `kvm_text`. Legacy setup is implemented by `syz_kvm_setup_cpu()`. SYZOS VM setup uses `kvm_syz_vm`, `addr_size`, `alloc_guest_mem`, `vm_set_user_memory_region`, `validate_guest_code`, `install_syzos_code`, `mem_region`, `syzos_mem_regions`, `setup_vm`, `syz_kvm_setup_syzos_vm`, `reset_cpu_regs`, `install_user_code`, and `syz_kvm_add_vcpu`. `syz_kvm_assert_reg` and `syz_kvm_assert_syzos_uexit` provide validation pseudo-syscalls.

## Control Flow

The legacy `syz_kvm_setup_cpu()` maps 24 pages at `RISCV64_ADDR_USER_CODE`, copies the user text into the first page, installs `guest_unexp_trap` into the next page as STVEC target, and initializes PC, SP, S-mode, SSTATUS, STVEC, and GP. The SYZOS path stores a `kvm_syz_vm` header in the first host page, uses the rest as guest backing memory, iterates `syzos_mem_regions`, skips MMIO/no-host-memory ranges, allocates backing for mapped ranges, copies exception-vector code or SYZOS executor code where needed, records the user-code host slot, and maps any remaining backing at GPA 0.

`syz_kvm_add_vcpu()` validates the VM pointer and CPU limit, creates a KVM vCPU with the next id, increments only on success, installs one page of user code into that CPU's slot, and calls `reset_cpu_regs()`. `reset_cpu_regs()` points PC at `guest_main` inside the executor code, sets stack and TP, passes text size and CPU id in A0/A1, enters S-mode, sets SSTATUS, GP, and STVEC to the exception vector page. Assertions read KVM one-reg values or validate MMIO uexit shape and code.

## State and Persistence Behavior

`kvm_syz_vm` persists in host memory and tracks `vmfd`, `next_cpu_id`, backing memory pointer, total page count, and the host address of the per-vCPU user-code region. Guest memory persists in the caller's mapping once registered with KVM. The code uses a bump allocator during setup only; no runtime host allocation is performed. vCPU state persists in KVM registers and CSRs.

## Dependencies and Integration Points

The header includes `common_kvm.h`, `kvm.h`, Linux ioctl definitions, and conditionally `common_kvm_riscv64_syzos.h` for guest symbols. Address constants for CLINT, PLIC, exit, dirty pages, user code, executor code, scratch, stacks, and exception vectors must match `kvm.h` and syzkaller syscall descriptions. The command ABI is coupled to `dev_kvm_riscv64.txt`.

## Risks and Edge Cases

`validate_guest_code()` rejects AUIPC instructions because copied SYZOS code cannot use data relocations; this protects against globals, constants, and jump-table emission. Several `KVM_SET_USER_MEMORY_REGION` calls ignore ioctl errors. Legacy setup copies `guest_unexp_trap` based on guest-section symbol distance and clamps by page size. SYZOS setup reserves the first host page for `kvm_syz_vm`, so total guest backing is `KVM_GUEST_PAGES - 1`. The user text is truncated to one page per vCPU. Register ids and CSR indices must match the kernel KVM RISC-V ABI.

## Test Signals

Coverage should include executor/csource builds, AUIPC rejection for relocated guest code, legacy one-vCPU boot to S-mode, STVEC unexpected-trap SBI exit, SYZOS VM setup with all mapped regions, multi-vCPU creation up to `KVM_MAX_VCPU`, per-vCPU user-code isolation, dirty-log region behavior, register assertions, and uexit assertions for both wrong MMIO metadata and wrong exit code.
