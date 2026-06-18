# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zgeneric.c

Generic PostScript operators for arrays, strings, dictionaries, and packed arrays. It implements `copy`, `forall`, `.forceput`, `get`, `getinterval`, `length`, `put`, and `putinterval`, plus continuation operators used by `forall`.

`zcopy` dispatches either to stack copying for integer operands or object copying for composite operands. `copy_interval` performs overlap-aware copying for array/string/packed-array intervals and uses `ref_assign_old` where write barriers are needed. `zget`, `zput`, `zgetinterval`, and `zputinterval` handle type-specific access rules for dictionaries, strings, arrays, and packed arrays, including read/write checks and range checks.

`zforall` schedules iteration on the execution stack. Separate continuations handle arrays, dictionaries, packed arrays, and strings, pushing the next value/key-value pair and re-scheduling the procedure until complete. `forall_cleanup` removes execution-stack state if an iteration aborts. The file is central interpreter collection logic and relies heavily on stack discipline, access attributes, VM-space checks, and packed-array decoding.
