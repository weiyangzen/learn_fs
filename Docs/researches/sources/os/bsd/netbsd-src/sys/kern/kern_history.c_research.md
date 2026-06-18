# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_history.c

Read completely: 562 lines.

Implements kernel history diagnostics: DDB dumping for `kern_history` ring buffers and a `kern.hist.*` sysctl export format that serializes events plus a compact string table for userland. It is enabled by build options such as `KERNHIST`, `UVMHIST`, `USB_DEBUG`, `BIOHIST`, and `SYSCALL_DEBUG`.

Core state:
- `kern_histories` is the global list of registered histories.
- `kernhist_sysctl_ready` gates sysctl node creation until `sysctl_kernhist_init()` has created `kern.hist`.
- `kernhist_print_enabled` controls printing behavior.
- `sysctl_hist_node` stores the created `kern.hist` node id.

DDB support:
- `kernhist_info()` prints metadata for one history.
- `kernhist_dump()` walks one ring buffer from either its oldest entry or the last `count` entries and prints nonempty events with `kernhist_entry_print()`.
- `kernhist_dump_histories()` merges multiple histories by event bintime, repeatedly printing the earliest current event across all selected histories.
- `kernhist_dumpmask()` builds a list of selected built-in histories from a bitmask and dumps them merged.
- `kernhist_print()` is the DDB hook: with modifier `i` it prints info, otherwise it dumps either the specified history or built-in histories.

Sysctl support:
- `sysctl_kernhist_init()` creates `kern.hist`, marks sysctl ready with a producer memory barrier, and calls `sysctl_kernhist_new(NULL)` to create nodes for existing histories.
- `sysctl_kernhist_new()` creates a `CTLTYPE_STRUCT` node for any history that lacks one, after a consumer barrier confirms sysctl readiness.
- `sysctl_kernhist_helper()` rejects writes, validates the sysctl path, finds the matching history, builds a translation table of unique function/format/name strings, allocates an output `struct sysctl_history`, copies event data and string offsets, appends the string table, copyouts as much as the caller requested, and reports required size through `oldlenp`.

String-table mechanics:
- `find_string()` matches strings by address and length rather than content.
- `add_string()` appends unique address/length pairs and precomputes offsets for the final output buffer.
- Offset zero is reserved for null/unused event fields; a `"?"` fallback string is added first for entries that appear after the unique-string pass due to concurrent history updates.

Concurrency and assumptions:
- DDB paths assume the system is quiesced and do no locking.
- Sysctl export does not lock the history while taking two passes; it tolerates concurrent updates by mapping unexpected strings to the fallback entry.
- Memory barriers around `kernhist_sysctl_ready` coordinate late history registration with sysctl initialization.

Risks and notes:
- The sysctl helper allocates based on worst-case two strings per event plus name/fallback and returns `ENOMEM` when the caller buffer is too small after partial copyout.
- Merged DDB dumping ignores the `count` parameter in `kernhist_dump_histories()`.
- The source comment for `sysctl_kernhist_init()` says `hw.hist`, but the code creates `kern.hist`.
