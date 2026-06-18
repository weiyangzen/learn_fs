<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/269 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/269

## Purpose
This related RCU stall fixture covers KVM instruction emulation and guest-memory reads. It should normalize to `INFO: rcu detected stall in kvm_vcpu_ioctl`, alt `stall in kvm_vcpu_ioctl`, and type `HANG`.

## Important APIs, Types, and Functions
The raw log contains `rcu_preempt detected stalls on CPUs/tasks` and a KVM call trace. Parser paths include RCU stall matching, task-stack extraction, and hang-title normalization. Key symbols include `sched_show_task`, `print_other_cpu_stall`, `rcu_check_callbacks`, `__virt_addr_valid`, `__check_object_size`, `__kvm_read_guest_page`, `kvm_fetch_guest_virt`, `x86_decode_insn`, `x86_emulate_instruction`, `kvm_mmu_page_fault`, `vcpu_enter_guest`, `kvm_arch_vcpu_ioctl_run`, and `kvm_vcpu_ioctl`.

## Control Flow
The reporter reads the RCU stall header and task stack, skips IRQ and RCU helper frames, then follows the KVM stack to the vCPU ioctl interface for the title.

## State and Persistence Behavior
The fixture is immutable raw log data with expected title, alt, and HANG type. It has no runtime state.

## Dependencies and Integration Points
It depends on RCU stall parser rules, KVM stack frame scoring, and generic `ParseTest` comparison.

## Risks and Edge Cases
Several KVM internals are more specific than `kvm_vcpu_ioctl`, but the expected title intentionally groups the hang at the user-facing ioctl boundary.

## Test Signals
The parse must return the KVM vCPU ioctl RCU-stall title and alt with type `HANG`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/269 -->
