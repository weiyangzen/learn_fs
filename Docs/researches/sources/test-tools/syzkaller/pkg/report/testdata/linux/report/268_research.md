<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/268 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/268

## Purpose
This fixture verifies RCU-preempt self-detected stall parsing in KVM vCPU ioctl execution. The expected title is `INFO: rcu detected stall in kvm_vcpu_ioctl`, alt `stall in kvm_vcpu_ioctl`, and type `HANG`.

## Important APIs, Types, and Functions
Headers include `TITLE`, `ALT`, and `TYPE`. Parser paths include RCU stall matching, grace-period kthread stack handling, IRQ-boundary stack parsing, and hang title generation. Important symbols include `rcu_gp_kthread`, `rcu_dump_cpu_stacks`, `print_cpu_stall`, `kvm_mmu_page_fault`, `handle_ept_violation`, `vmx_handle_exit`, `vcpu_enter_guest`, `kvm_arch_vcpu_ioctl_run`, `kvm_vcpu_ioctl`, `do_vfs_ioctl`, and `__x64_sys_ioctl`.

## Control Flow
The reporter first sees an RCU grace-period kthread stack, then the stalled CPU/task stack in KVM. It must ignore the kthread diagnostic stack for titling and choose the KVM ioctl frame from the actual stalled task.

## State and Persistence Behavior
The file stores a raw RCU stall log and expected HANG metadata. It has no mutable state.

## Dependencies and Integration Points
It depends on Linux RCU stall parsing, stack section selection, and hang crash-type mapping.

## Risks and Edge Cases
The first available stack is not the bug site. If the parser selects `rcu_gp_kthread` or `kvm_mmu_page_fault`, this fixture catches the regression.

## Test Signals
Expected output is title `INFO: rcu detected stall in kvm_vcpu_ioctl`, alt `stall in kvm_vcpu_ioctl`, and type `HANG`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/268 -->
