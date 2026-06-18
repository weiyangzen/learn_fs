<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/273 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/273

## Purpose
This fixture is another KVM RCU stall variant, this time with `__srcu_read_lock` at the stalled RIP. It should still parse to `INFO: rcu detected stall in kvm_vcpu_ioctl`, alt `stall in kvm_vcpu_ioctl`, and type `HANG`.

## Important APIs, Types, and Functions
Parser paths include RCU detected-stalls matching, IRQ helper skipping, KVM stack frame selection, and hang title generation. Key symbols include `sched_show_task`, `print_other_cpu_stall`, `rcu_check_callbacks`, `__srcu_read_lock`, `vcpu_enter_guest`, `kvm_arch_vcpu_ioctl_run`, `kvm_vcpu_ioctl`, `do_vfs_ioctl`, `ksys_ioctl`, `__x64_sys_ioctl`, and `do_syscall_64`.

## Control Flow
The reporter reads the RCU stall header and task stack. Although `__srcu_read_lock` is the immediate RIP, the parser must walk outward to the KVM vCPU ioctl path for the stable title.

## State and Persistence Behavior
The source persists the expected HANG title, alt, and raw log. It has no runtime state.

## Dependencies and Integration Points
It depends on RCU stall parsing and KVM frame-priority rules shared with reports 268 and 269.

## Risks and Edge Cases
The stall is inside SRCU rather than a KVM MMU helper, so naive first-frame selection would regress the title to a generic synchronization primitive.

## Test Signals
Expected output is the KVM vCPU ioctl RCU-stall title and alt with type `HANG`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/273 -->
