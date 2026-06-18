# File Research: sources/os/linux/linux/mm/kfence/report.c

## Role

KFENCE report generation and object-info formatting. It prints console reports, object allocation/free histories, canary corruption details, fault handling outcomes, and printk object metadata integration.

## Key Functions

- Parses `kfence.fault=report|oops|panic`.
- `seq_con_printf()` writes to either a `seq_file` or the console.
- `get_stack_skipnr()` skips KFENCE/slab allocator internals to show the relevant caller frame.
- `kfence_print_stack()` prints allocation/free/RCU-freeing task, CPU, timestamp, elapsed time, and filtered stack entries.
- `kfence_print_object()` prints guarded object index, address range, size, cache name, and alloc/free stacks.
- `print_diff_canary()` shows changed canary bytes while avoiding object contents and pointer leaks unless `no_hash_pointers` permits raw values.
- `kfence_report_error()` captures a stack trace, disables lockdep for printing, emits a typed report header, prints stack and object metadata, emits error trace event, checks `panic_on_warn`, taints the kernel, and returns the configured fault action.
- `kfence_handle_fault()` implements report/no-op, `BUG()`, or panic behavior; panic disables KFENCE first to avoid recursion.
- Under `CONFIG_PRINTK`, `__kfence_obj_info()` fills `kmem_obj_info` for printk object diagnostics.

## Error Types

Reports distinguish:

- out-of-bounds read/write;
- use-after-free read/write;
- canary memory corruption;
- invalid read/write;
- invalid free.

## Dependencies

Uses stack trace helpers, scheduler clock, printk, panic/oops paths, lockdep, seq files, KFENCE metadata, architecture function-prefix support, and `trace/events/error_report.h`.

## Research Notes

KFENCE reporting intentionally accepts printk risk in difficult contexts to surface memory-safety failures. It narrows report stacks to user-relevant call sites and prints both allocation and deallocation history when metadata state allows.
