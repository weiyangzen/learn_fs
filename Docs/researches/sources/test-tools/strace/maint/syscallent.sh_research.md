# sources/test-tools/strace/maint/syscallent.sh

Purpose: builds syscall table initializer rows from `SYS_*` or `__NR_*` numeric definitions.

Important APIs/types/functions: sed patterns for direct numeric defines and `__NR_Linux + offset`, numeric sort/uniq, and awk output using `printargs` placeholders for gaps and `sys_<name>` decoder functions for known calls.

Control flow: read headers from arguments/stdin, extract syscall names/numbers, sort, emit placeholder rows until each syscall number is reached, emit the syscall row, then append 100 trailing placeholder entries after the last known syscall.

State and persistence behavior: stdout only.

Dependencies and integration points: historical architecture syscall table generation; output shape matches strace `sysent` initializer format.

Risks: parser only sees simple numeric forms and may not correctly handle aliases or complex macro arithmetic. The trailing 100 placeholders are a convention that can drift from modern table needs.

Test signals: generated syscall tables should compile and resolve known syscall numbers for the target architecture.
