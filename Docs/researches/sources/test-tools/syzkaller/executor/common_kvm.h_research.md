# sources/test-tools/syzkaller/executor/common_kvm.h

Purpose: This shared KVM header provides architecture-neutral syzkaller KVM helpers used by SYZOS guest support and KVM pseudo-syscalls.

Important APIs and types: It includes `common_kvm_syzos.h` and `kvm.h`, declares `extern char* __start_guest`, defines `executor_fn_guest_addr`, and implements `syz_kvm_assert_syzos_kvm_exit`. In executor C++ builds, a template overload restricts `executor_fn_guest_addr` to guest-address-space function pointers.

Control flow and state: `executor_fn_guest_addr` converts a host-linked guest function address into the runtime guest physical/virtual address by subtracting `&__start_guest` and adding `SYZOS_ADDR_EXECUTOR_CODE`; volatile temporaries prevent unwanted constant materialization. `syz_kvm_assert_syzos_kvm_exit` validates that a `struct kvm_run` exists and that `exit_reason` equals the expected value, returning `-1` with `EINVAL` or `EDOM` on failure and optionally printing debug details in csource mode.

Dependencies and integration points: It is included by architecture-specific KVM headers such as `common_kvm_amd64.h`. It depends on KVM UAPI structures, SYZOS linker symbols, errno, and generated pseudo-syscall gating macros.

Risks and test signals: Risks include incorrect guest address relocation if linker symbols or `SYZOS_ADDR_EXECUTOR_CODE` drift, and assertion helpers being compiled differently between executor and csource. Tests should validate guest function address translation against installed executor-code memory and assert helpers for matching, mismatching, and null `kvm_run` inputs.
