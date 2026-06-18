# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/interp.c

Main Ghostscript language interpreter implementation. It owns interpreter initialization/reset, stack allocation, optimized operator dispatch, execution of refs and packed refs, scanner integration, error recovery, garbage collection signaling, time slicing, and internal oparray stack-protection operators.

Key behavior:
- Registers GC descriptors for dictionary, execution, and operand stacks.
- Defines default reschedule and optional time-slice hooks.
- Defines hard-coded fast operator pseudo-types for common operators: `add`, `def`, `dup`, `exch`, `if`, `ifelse`, `index`, `pop`, `roll`, and `sub`.
- Exposes `gs_interp_max_op_num_args`, `gs_interp_num_special_ops`, and `tx_next_index`.
- Defines `interp_op_defs`, including special operators plus internal `.currentstackprotect`, `.setstackprotect`, `%interp_exit`, and `%oparray_pop`.
- `gs_interp_init` allocates and loads an interpreter context.
- `gs_interp_alloc_stacks` allocates operand, execution, and dictionary stacks from stable memory with guard slots, error codes, and maximum counts.
- `gs_interp_free_stacks` releases stacks in inverse order.
- `gs_interp_reset` clears operand/execution stacks, installs `%interp_exit`, resets dictionary stack to the minimum depth, and refreshes dictionary cache state.
- `gs_interp_make_oper` assigns special extended types to hard-coded fast operators.
- `interp_reclaim` invokes the allocator GC hook while rooting the interpreter context pointer.
- `gs_interpret` roots the returned error object, delegates to `gs_call_interp`, and clears GC signal pointers before returning.
- `gs_call_interp` wraps the core loop with GC retry, stack overflow/underflow recovery, error-object handling, quit/fatal handling, and errordict dispatch.
- `set_gc_signal` installs or clears a GC signal pointer across all VM spaces and stable-memory allocators.
- `copy_stack` copies an overflowed stack into a local array for error reporting.
- `gs_errorname` maps error codes through `systemdict /ErrorNames`.
- `gs_errorinfo_put_string` stores a string in `$error /errorinfo`.
- The private `interp` loop dispatches literal refs, executable arrays, names, files, strings, packed integers, packed names, packed executable operators, and packed/full refs.
- Executable files and strings are scanned through `scan_token`; EOF, refill, comments, DSC comments, and binary object sequences are handled specially.
- Packed arrays use `ipacked.h` encoding and can execute packed special operators directly when `PACKED_SPECIAL_OPS` is enabled.
- `e_RemapColor`, `o_push_estack`, `o_pop_estack`, `o_reschedule`, interrupts, GC thresholds, and time slices all store enough execution state to resume.
- `oparray_pop`, `oparray_cleanup`, `.setstackprotect`, and `.currentstackprotect` manage stack restoration policy for pseudo-operator arrays.

Notable dependencies:
- Interpreter stack APIs: `estack.h`, `ostack.h`, `dstack.h`, `istack.h`.
- Memory and GC APIs: `ialloc.h`, `iastruct.h`, `ivmspace.h`, `gsstruct.h`.
- Name/dictionary APIs: `iname.h`, `inamedef.h`, `iddict.h`.
- Scanner/token APIs: `iscan.h`, `itoken.h`, `files.h`, `stream.h`, `sfilter.h`.
- Operator APIs: `oper.h`, `opdef` data, and operator implementations declared elsewhere.
- Packed ref definitions from `ipacked.h`.

Research notes:
- This is the central interpreter execution engine and one of the most performance-sensitive files in the subtree.
- The dispatch loop is heavily macro- and goto-based to preserve old compiler performance and handle packed refs without excessive branching.
- Several comments document compiler and architecture workarounds, especially around unaligned packed refs and aliasing assumptions.
- Execution stack expansion is explicitly marked not implemented; overflow is handled by error/reporting paths rather than normal extension.
- Some comments mark known questionable areas, such as handling `e_ExecStackUnderflow`, ignored negative `context_state_store/load` codes during GC, and disabled time-slice jumps for operators.
