# File Research: sources/os/plan9/9front/sys/src/cmd/awk/run.c

This is the runtime executor for the 9front/Lucent awk interpreter. It walks the parsed `Node` tree through `execute`, dispatches parse operators through `proctab`, and maintains awk control-flow sentinels for `break`, `continue`, `next`, `nextfile`, `return`, and `exit`.

Major responsibilities:
- Program execution: `run`, `execute`, `program`.
- User function calls: stack frames in `struct Frame`, argument copying/reference handling, return values.
- Expression evaluation: arithmetic, assignment, concatenation, relation/boolean operators, conditional expressions.
- Arrays: multi-subscript key construction using `SUBSEP`, delete, membership tests, `for (x in a)`.
- Builtins: `length`, math functions, `system`, `rand/srand`, case conversion, `fflush`, UTF rune conversion.
- I/O: `getline`, `print`, `printf`, redirections, pipes via `popen`, close/flush tracking through a fixed `files[FOPEN_MAX]` table.
- String operations: UTF-aware `substr`/`index`, `split`, `sub`, `gsub`, replacement escape handling.

Filesystem/OS relevance:
- Uses Plan 9 `Biobuf`, `/bin/rc -c` for `system`, file descriptors, pipes, and path-like redirection names.
- Redirection state is process-global and bounded by `FOPEN_MAX`.

Notable implementation details:
- Uses `setjmp/longjmp` for awk `exit`.
- Field/record coherence is lazy through `donefld`, `donerec`, `fldbld`, `recbld`.
- `adjbuf` centralizes dynamic output-buffer growth.
- UTF handling appears in match positions, case conversion, `substr`, `split("", ...)`, and `%c`.

Risks and caveats:
- Function-call logic is explicitly described as fragile and has comments about possible double frees.
- Several fixed-size or bounded resources remain: open file table, temp cell block allocation, format-number sizing.
- `system` waits for the exact child and treats any non-empty wait message as failure.
