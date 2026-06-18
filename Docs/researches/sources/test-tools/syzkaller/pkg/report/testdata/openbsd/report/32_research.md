# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/32

Purpose: Full OpenBSD page-fault fixture with DDB trace and symbolized source locations. Expected title is `uvm_fault: pfsync_state_import`.

Important parser APIs and patterns: uses the `uvm_fault(` oops group title rule that finds `Stopped at` and formats `uvm_fault: %[1]v`. Stack symbolization/recognition uses OpenBSD frames such as `pfsync_state_import(...) at pfsync_state_import+0x10f`.

Control flow: the crash starts with `uvm_fault(...) -> e`, `kernel: page fault trap`, and `Stopped at pfsync_state_import+0x10f`. DDB then runs `show panic`, `trace`, `show registers`, `ps`, `show malloc`, and CPU trace commands. Primary execution flows from `pfsync_state_import` through `pfioctl`, vnode ioctl wrappers, and syscall.

State and persistence: static fixture containing register state (`r15` is zero at the fault), process tables, allocator statistics, and repeated CPU traces.

Dependencies and integration: tests OpenBSD fault extraction with complete DDB context and source-line-enriched stack frames.

Risks: duplicate traces and failed `machine ddbcpu` commands can confuse report-end logic. The title must select the stopped function, not later repeated stack frames.

Test signals: exact title `uvm_fault: pfsync_state_import`; stack path includes `pfioctl` and `sys_ioctl`.
