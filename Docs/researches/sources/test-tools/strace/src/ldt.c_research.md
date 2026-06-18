# sources/test-tools/strace/src/ldt.c

Purpose: decodes architecture-specific LDT/thread-area syscalls, especially x86 `struct user_desc`.

Important APIs/types/functions: `print_user_desc`, `SYS_FUNC(modify_ldt)`, `SYS_FUNC(set_thread_area)`, `SYS_FUNC(get_thread_area)`, `USER_DESC_ENTERING`, `USER_DESC_EXITING`, `USER_DESC_BOTH`, `set_tcb_priv_data`, and `tcp->auxstr`.

Control flow: when `HAVE_STRUCT_USER_DESC` is available, `print_user_desc` can print entry number on entry, full descriptor on exit, or the whole structure at once. `modify_ldt` prints function, pointer/descriptor, bytecount, and adjusts x86_64 clipped negative return values into syscall errors. `set_thread_area` prints the descriptor and on successful exit attaches returned entry number. `get_thread_area` splits descriptor printing across entry and exit. M68K/MIPS provide simple address decoders.

State and persistence behavior: `get_thread_area` stores the original `entry_number` in `tcb` private data for exit comparison. `set_thread_area` uses static `outstr` for the auxiliary return string. No durable global state.

Dependencies and integration points: depends on `<asm/ldt.h>`, `xstring.h`, architecture macros, verbose/syserror state, and syscall table selection for thread-area APIs.

Risks: field availability differs by architecture and `lm` is only meaningful for 64-bit kernel-long size. `modify_ldt` return-error rewriting is x86 ABI-specific and easy to regress.

Test signals: cover `modify_ldt` with descriptor-sized and non-descriptor buffers, clipped negative return values, `set_thread_area` returned entry number, `get_thread_area` value changes, missing/inaccessible descriptors, and M68K/MIPS simple decoders.
