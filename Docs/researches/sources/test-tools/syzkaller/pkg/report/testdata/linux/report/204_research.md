<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/204 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/204

## Purpose
This short fixture validates warning parsing for an oversized or invalid kmalloc request in KVM VM ioctl handling. Expected title is `WARNING: kmalloc bug in kvm_vm_ioctl`, type `WARNING`.

## Important APIs, Types, And Functions
The 38-line report includes `WARNING: CPU ... at mm/slab_common.c:903 kmalloc_slab` and stack frames `warn_alloc`, `__vmalloc_node_range_memcg`, `vmalloc`, `kvm_vm_ioctl`, `do_vfs_ioctl`, `SyS_ioctl`, and `entry_SYSCALL_64_fastpath`. Parser behavior includes kmalloc warning recognition and caller-title selection.

## Control Flow
The Linux reporter should scan the warning and use `kvm_vm_ioctl` as the subsystem caller, not the generic slab helper. Runtime flow is a user ioctl on a KVM VM file causing memory allocation logic to warn.

## State And Persistence
The fixture persists expected title/type and a compact warning trace. Dynamic state includes PID, allocation size/mode details, addresses, and ioctl arguments if present.

## Dependencies And Integration Points
It depends on Linux warning parser rules, slab/kmalloc message handling, and KVM ioctl stack title heuristics. It integrates with standard syzkaller report tests.

## Risks
The parser could emit `WARNING in kmalloc_slab`, `WARNING in vmalloc`, or fail because the trace is short. It should retain KVM context for deduplication value.

## Test Signals
Assert title `WARNING: kmalloc bug in kvm_vm_ioctl` and type `WARNING`; report text should contain the slab warning and KVM ioctl frame.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/204 -->
