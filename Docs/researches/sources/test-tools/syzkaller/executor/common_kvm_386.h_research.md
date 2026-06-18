# sources/test-tools/syzkaller/executor/common_kvm_386.h

Purpose: This 386 KVM header is a stub implementation for SYZOS/KVM pseudo-syscalls on 32-bit x86 builds.

Important APIs and types: It conditionally defines no-op versions of `syz_kvm_setup_syzos_vm`, `syz_kvm_add_vcpu`, `syz_kvm_assert_syzos_uexit`, `syz_kvm_assert_syzos_kvm_exit`, and `syz_kvm_setup_cpu`.

Control flow and state: Every function immediately returns `0` regardless of input. No KVM ioctls are issued, no VM/VCPU state is created, and no memory is touched. Compile-time `SYZ_EXECUTOR` or generated syscall-number macros control whether each stub is present.

Dependencies and integration points: It exists so common generated KVM pseudo-syscall names can compile for 386 even though the substantive implementation lives in amd64-specific support. It depends only on surrounding typedefs/macros from the executor environment.

Risks and test signals: The main risk is semantic mismatch: a caller might treat success return values as real KVM setup even though nothing happened. Tests should confirm 386 builds compile, KVM pseudo-syscalls are either not generated for unsupported targets or documented as inert, and no downstream path dereferences a stub “VM” result as a real object.
