<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/201 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/201

## Purpose
This fixture covers a corrupted general protection fault in IPsec/pfkey processing. Expected title is `general protection fault in corrupted`, alt `bad-access in corrupted`, type `DoS`, with both `CORRUPTED` and `PANICKED` set.

## Important APIs, Types, And Functions
The log contains KASAN-enabled GPF text plus `BUG: using __this_cpu_read() in preemptible ...` and a panic. Important frames include `check_preemption_disabled`, `__this_cpu_preempt_check`, `ipcomp_init_state`, `ipcomp6_init_state`, `__xfrm_init_state`, `xfrm_init_state`, `pfkey_add`, `pfkey_process`, `pfkey_sendmsg`, `sock_sendmsg`, `___sys_sendmsg`, `__sys_sendmsg`, `compat_SyS_sendmsg`, and `entry_SYSENTER_compat`, with later SCSI cleanup frames such as `sg_remove_scat.isra.19`.

## Control Flow
The reporter should identify the GPF as corrupted rather than assigning a precise IPsec title. The runtime path is compat sendmsg into PF_KEY state creation and XFRM/IPComp initialization, followed by fatal exception panic and unrelated cleanup noise.

## State And Persistence
Persistent state is the expected corrupted title, type, panic/corruption flags, and 118-line log. Dynamic state includes preemption state, task IDs, register values, and protocol state addresses.

## Dependencies And Integration Points
It depends on Linux GPF parsing, corrupted-log heuristics, preemption warning handling, compat syscall frame parsing, and panic detection. It integrates with report tests as a noisy corrupted DoS case.

## Risks
The parser could choose `ipcomp_init_state`, `pfkey_add`, or `__this_cpu_preempt_check` as the title, losing the expected corrupted classification. It could also misclassify the preemption warning as the primary bug.

## Test Signals
Stable checks are title `general protection fault in corrupted`, alt `bad-access in corrupted`, type `DoS`, `CORRUPTED: Y`, and `PANICKED: Y`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/201 -->
