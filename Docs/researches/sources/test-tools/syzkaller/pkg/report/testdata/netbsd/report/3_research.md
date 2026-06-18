# sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/3

## Purpose

`sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/3` is a NetBSD syzkaller report parser fixture for the expected title `page fault in __asan_load8`. It records a KASAN/ASan-instrumented NetBSD kernel page fault while servicing `ptrace`, with source-line annotations for the ASan helper and ptrace path. The source was read as a complete 1431-line file: high-value parser data appears in the initial fatal page fault, stopped instruction, stack trace with inline source locations, register dump, process/LWP table, lockdebug sections, and the later repetitive page metadata dump.

## Important APIs, Types, and Functions

This is static parser testdata, not executable code. The relevant syzkaller APIs are the generic report test flow, `Reporter.ContainsCrash`, `Reporter.Parse`, `Reporter.ParseFrom`, title extraction from the `TITLE:` header, and NetBSD-specific oops/frame selection logic. Kernel symbols and implementation details represented in the transcript include `__asan_load8`, `kasan_shadow_8byte_isvalid`, `kasan_shadow_check`, `ptrace_machdep_dorequest`, `do_ptrace`, `sys_ptrace`, `sys___syscall`, and `syscall`. Source paths embedded in the stack include `sys/kern/subr_asan.c`, `sys/arch/amd64/amd64/process_machdep.c`, `sys/kern/sys_ptrace_common.c`, `sys/kern/sys_ptrace.c`, `sys/kern/sys_syscall.c`, `sys/sys/syscallvar.h`, and `sys/arch/x86/x86/syscall.c`.

## Control Flow

The test harness parses the title header, then asks the NetBSD reporter to detect and summarize the console body. The parser must classify the `fatal page fault in supervisor mode`, extract `__asan_load8` from the stopped line and stack, and handle inline annotation suffixes without polluting the title. The kernel-side path is syscall entry for syscall number 198 -> `sys___syscall` -> `sys_ptrace` -> `do_ptrace` -> `ptrace_machdep_dorequest` -> ASan instrumentation helper `__asan_load8`, which faults while checking an address associated with `rax = ffff900000000000` and `cr2 = 0xffff900000000000`.

## State and Persistence Behavior

The file persists expected parser behavior through the `TITLE:` line plus a raw kernel debugger transcript. Runtime parser state is ephemeral: report boundaries, selected frame, source-location trimming, title, crash type, and parse offsets. The kernel transcript includes volatile state such as register values, LWP structures, syz executor instances, lock owner addresses, CPU IDs, and `uvm_obj_init` lockdebug records. These fields are useful for parser coverage but should remain report body details rather than title keys.

## Dependencies and Integration Points

The fixture integrates with the NetBSD reporter's support for fatal page faults, KASAN/ASan helper frames, inline source annotations, ptrace stack traces, lockdebug output, process tables, and long debugger tails. It also exercises the generic report package's stack-frame sanitization and crash deduplication contract: sanitizer helper names are sometimes real top frames and must be preserved when they are the actual stopped frame. The downstream integration point is syzkaller dashboard grouping for NetBSD ASan faults in architecture-specific ptrace code.

## Risks and Edge Cases

The key parser risk is confusing sanitizer helper frames with ignorable diagnostic helpers. In this fixture, `__asan_load8` is the expected title because the CPU stopped in that function, even though inline lines mention `kasan_shadow_8byte_isvalid` and `kasan_shadow_check`. The parser must strip source-line suffixes, avoid volatile addresses, and not retitle the crash as `ptrace_machdep_dorequest` or `do_ptrace`. It must also tolerate lockdebug sections, two executor LWPs marked with `>`, held `uvm_obj_init` locks, `Turnstile` text, and a long page metadata tail without creating secondary crashes.

## Test Signals

A passing test detects a crash and returns exactly `page fault in __asan_load8` with non-empty report bytes. Strong signals include correct handling of `kernel: page fault trap, code=0`, preservation of the ASan top frame despite inline annotations, stable parse offsets across `ParseFrom`, and ignoring lockdebug/page-table noise. Regression tests should fail if a parser starts choosing ptrace wrapper frames, source file paths, raw addresses, or repeated `PAGE FLAG` rows for the title.
