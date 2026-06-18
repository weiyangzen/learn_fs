# sources/test-tools/syzkaller/executor/common_kvm_arm64.h

## Purpose

`common_kvm_arm64.h` is the host-side ARM64 implementation of syzkaller KVM pseudo-syscalls. It maps the guest physical layout expected by ARM64 SYZOS, installs the guest runtime into KVM memory, initializes vCPU registers, loads per-vCPU user programs, creates additional SYZOS vCPUs, sets up a VGICv3 device, and exposes assertion helpers for uexit and register values.

## Important APIs, Types, and Functions

`kvm_text` and `kvm_opt` are the user command descriptors. Memory setup is handled by `addr_size`, `alloc_guest_mem`, `vm_set_user_memory_region`, `validate_guest_code`, `install_syzos_code`, and `setup_vm`. vCPU setup uses `vcpu_set_reg`, `reset_cpu_regs`, `install_user_code`, and `setup_cpu_with_opts`. Public pseudo-syscall entry points are `syz_kvm_setup_cpu`, `syz_kvm_setup_syzos_vm`, `syz_kvm_add_vcpu`, `syz_kvm_vgic_v3_setup`, `syz_kvm_assert_syzos_uexit`, and `syz_kvm_assert_reg`.

## Control Flow

`syz_kvm_setup_cpu()` reads the first `kvm_text`, maps the whole SYZOS VM layout with `setup_vm()`, initializes the vCPU target with optional feature bits, copies the user code into CPU 0's user page, and sets PC/SP/TPIDR_EL1/X0/X1 for `guest_main`. `syz_kvm_setup_syzos_vm()` stores a small `kvm_syz_vm` control block in the first host page, maps the rest as guest memory, and returns that control block to the fuzzer. `syz_kvm_add_vcpu()` creates the next KVM vCPU, applies the same CPU init, installs that CPU's code page, increments `next_cpu_id` only after successful creation, and returns the vCPU fd.

`setup_vm()` uses a simple bump allocator over `KVM_GUEST_MEM_SIZE`, maps the executor guest code read-only at `SYZOS_ADDR_EXECUTOR_CODE`, dirty-log pages at `ARM64_ADDR_DIRTY_PAGES`, per-vCPU user code read-only at `ARM64_ADDR_USER_CODE`, stack and scratch pages, ITS tables, and finally any remaining pages at GPA 0. VGIC setup creates `KVM_DEV_TYPE_ARM_VGIC_V3`, configures IRQ count, distributor address, redistributor region, and initializes the device. Assertions validate MMIO uexit shape and expected code or read one KVM one-reg value.

## State and Persistence Behavior

Host-visible state is the `kvm_syz_vm` record containing `vmfd`, `next_cpu_id`, and the host pointer for the user-text slot. Guest memory contents persist in the caller-provided `host_mem` backing area after registration with KVM. `setup_vm()` is destructive with respect to the supplied memory because it copies SYZOS code and later user code into fixed offsets. There is no filesystem persistence and no dynamic allocation beyond slicing the provided mapping.

## Dependencies and Integration Points

The header includes `common_kvm.h`, `kvm.h`, Linux KVM ioctls, and conditionally `common_kvm_arm64_syzos.h` so host setup can reference `__start_guest`, `__stop_guest`, `guest_main`, and `executor_fn_guest_addr`. It depends on ARM64 constants in `kvm.h` for GIC, dirty page, scratch, stack, user-code, ITS, and SYZOS code addresses. The pseudo-syscall signatures are coupled to syzkaller `dev_kvm_arm64.txt` descriptions.

## Risks and Edge Cases

`validate_guest_code()` rejects ADRP instructions because the SYZOS copy path does not process relocations; this catches global-data and jump-table regressions early. Most `ioctl()` calls in memory setup ignore return values, so failures can surface later as guest failures rather than immediate pseudo-syscall errors. `setup_cpu_with_opts()` accepts at most one option and only uses type 1 as ARM feature bits. User text count is ignored and only element 0 is consumed. `gicv3_enable_redist()` in the guest-side companion uses redistributor addresses that must stay consistent with this host mapping. The returned `kvm_syz_vm` lives inside the same host memory area used for guest backing, so the first page is reserved by convention.

## Test Signals

Build coverage should include executor and csource modes with each guarded pseudo-syscall enabled. Runtime signals are successful KVM memory registration, ADRP rejection for deliberately bad guest code, `syz_kvm_setup_cpu` booting one vCPU to `guest_main`, `syz_kvm_setup_syzos_vm` plus repeated `syz_kvm_add_vcpu` up to `KVM_MAX_VCPU`, VGICv3 creation and initialization, dirty-page logging on the dirty region, register assertions through `KVM_GET_ONE_REG`, and uexit assertion failures for wrong MMIO address or code.
