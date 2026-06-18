# File Research: sources/os/bsd/netbsd-src/sys/sys/exec_script.h

Read completely: 49 lines.

## Purpose
Defines shebang script exec recognition constants and the kernel script exec handler declaration.

## Main Interfaces
- `EXEC_SCRIPT_MAGIC` as `#!`.
- `EXEC_SCRIPT_MAGICLEN`.
- `SCRIPT_HDR_SIZE`, based on magic length, `MAXINTERP`, optional space, and newline.
- Kernel handler: `exec_script_makecmds`.

## Dependencies And Integration
Used by exec format dispatch after reading executable headers from a vnode.

## Risks And Edge Cases
- Interpreter parsing is bounded by `SCRIPT_HDR_SIZE`.
- Script indirection interacts with `EXEC_INDIR`, fake args, and held script descriptors in `exec.h`.

## Filesystem Relevance
High for script execution. It maps a file's first bytes to interpreter path lookup and exec recursion.
