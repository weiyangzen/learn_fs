<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/unwind.c -->
# sources/test-tools/strace/src/unwind.c

Purpose: Common stack-unwind orchestration layer: initializes backend hooks, manages per-tcb queued stack frames, formats/demangles entries, and captures/prints/discards call stacks.

Important APIs/types/functions:
- Helper functions include `unwind_init`, `unwind_tcb_init`, `unwind_tcb_fin`, `print_call_cb`, `print_error_cb`, `sprint_call_or_error`, `queue_put`, `queue_put_call`, `queue_put_error`, `queue_drain`, `unwind_tcb_print`, `unwind_tcb_discard`, `unwind_tcb_capture`
- Direct includes: `"defs.h"`, `"unwind.h"`, `<demangle.h>`, `<libiberty/demangle.h>`
- Local/exported macros: `LIBIBERTY_H`, `STACK_ENTRY_SYMBOL_WITH_SRCINFO_FMT`, `STACK_ENTRY_SYMBOL_FMT`, `STACK_ENTRY_NOSYMBOL_FMT`, `STACK_ENTRY_BUG_FMT`, `STACK_ENTRY_ERROR_WITH_OFFSET_FMT`, `STACK_ENTRY_ERROR_FMT`

Control flow:
- control flow is linear around a small decoder/helper surface and returns standard strace `RVAL_*` flags

State and persistence behavior:
- allocates temporary or per-tracee memory and releases it through explicit cleanup paths or tcb destructors
- uses static process-local configuration/cache data; no repository-persistent state is written

Dependencies and integration points:
- depends on strace `defs.h` formatting/fetch APIs and listed kernel/libc headers

Risks:
- length/count fields need bounds-aware printing to avoid misleading output or excessive tracee reads

Test signals:
- cover native and compat personality builds where available
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/unwind.c -->
