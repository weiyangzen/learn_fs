# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcontrol.c

Implements core Ghostscript/PostScript control operators around the operand stack and execution stack.

Key operators include `.cond`, `exec`, `.execn`, `superexec`, `.runandhide`, `if`, `ifelse`, `for`, `%for_samples`, `repeat`, `loop`, `exit`, `stop`, `.stop`, `stopped`, `.stopped`, `.instopped`, `countexecstack`, `execstack`, `.needinput`, `.quit`, and `currentfile`.

The implementation is continuation-heavy: `cond`, loops, `stopped`, `execstack`, `runandhide`, and sample iteration push continuation operators or marks onto the execution stack. Loop and stopped scopes are represented by estack marks such as `es_for` and `es_stopped`.

Important internal routines:
- `pop_estack()` unwinds execution stack entries and invokes cleanup procedures on marks.
- `count_to_stopped()` locates a matching stopped mark by signal mask.
- `count_exec_stack()` optionally hides executable null mark entries.
- `unmatched_exit()` converts unmatched `exit`/`stop` into an interpreter quit with `e_invalidexit`.

Security and correctness notes: `zexecn()` validates executable access before pushing objects to the execution stack; `do_execstack()` sanitizes internal operators and stack-associated structs before exposing stack contents; `.runandhide` temporarily removes an array from the operand stack and restores attributes on normal or error paths.

Registered operator tables are split into `zcontrol1_op_defs`, `zcontrol2_op_defs`, and `zcontrol3_op_defs` because of the operator table size limit.
