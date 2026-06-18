# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/interp.c

Ghostscript language interpreter implementation. It initializes interpreter stacks, defines special hard-coded operators, executes refs and packed refs, handles executable files/strings/procedures, coordinates errors, and invokes GC/time-slicing.

Key behavior:
- Defines GC descriptors for operand, execution, and dictionary stacks.
- Installs default reschedule/time-slice hooks, with rescheduling returning `invalidcontext` until context machinery replaces it.
- Defines fast special operator pseudo-types for `add`, `def`, `dup`, `exch`, `if`, `ifelse`, `index`, `pop`, `roll`, and `sub`.
- `gs_interp_init` allocates and loads context state.
- `gs_interp_alloc_stacks` allocates one stable ref array and partitions it into operand, execution, and dictionary stacks with guard zones and limits.
- `gs_interp_reset` clears operand/execution stacks, reinstalls `%interp_exit`, trims dict stack, and refreshes cached dictionary top.
- `gs_interp_make_oper` assigns hard-coded special operator types when possible.
- `interp_reclaim` calls the active dual-memory GC while registering the context pointer as a root.
- `gs_interpret` wraps `gs_call_interp`, roots the error object, and clears GC signal pointers afterward.
- `gs_call_interp` loops around the core interpreter, handling GC requests, `quit`, interpreter exit, VM reclaim, input-needed returns, stack growth/recovery, and errordict dispatch.
- `interp` is the main threaded dispatch loop. It:
  - keeps private operand and execution stack pointers for speed;
  - executes arrays, packed arrays, op arrays, names, operators, files, and strings;
  - uses cached name `pvalue` pointers and falls back to dictionary lookup by name index;
  - scans executable files and strings with `scan_token`;
  - handles binary object sequences, refill continuations, comments, and DSC comments;
  - directly decodes packed integers, names, and executable operators;
  - stores execution state back to the e-stack around calls, errors, and scheduling;
  - triggers time slicing or GC when `ticks_left` crosses thresholds.
- Error paths convert packed refs into full refs for `perror_object`, push interrupt objects back onto the execution stack, and log errors with source line information.
- Provides hidden stack-protection operators `.setstackprotect` and `.currentstackprotect` for `t_oparray` cleanup behavior.

Notable dependencies:
- Core interpreter state and stacks: `icontext.h`, `dstack.h`, `estack.h`, `ostack.h`.
- Object representation and packing: `iref.h`, `ipacked.h`.
- Name/dictionary machinery: `iname.h`, `inamedef.h`, `iddict.h`.
- Scanner/token handling: `iscan.h`, `itoken.h`, streams and filters.

Research notes:
- The loop is highly macro- and goto-driven for speed; packed-array and full-ref dispatch are intentionally interleaved.
- Several comments flag known limitations or fragile areas, including e-stack expansion being not implemented, an `ExecStackUnderflow` recovery comment marked wrong, and disabled time-slice jump experiments.
- The interpreter relies on exact type/attribute bit layout from `iref.h` and packed encoding from `ipacked.h`; changing either requires coordinated edits here.
