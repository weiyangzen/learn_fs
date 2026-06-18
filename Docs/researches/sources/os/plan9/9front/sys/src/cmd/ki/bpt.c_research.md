# File Research: sources/os/plan9/9front/sys/src/cmd/ki/bpt.c

Breakpoint management for the `ki` SPARC interpreter/debugger. It supports instruction breakpoints plus memory read, write, access, and “equal value” watchpoints. `breakpoint` parses the breakpoint modifier, evaluates the address expression, stores pass counts, and links into `bplist`; `delbpt` removes by address.

`brkchk` is called from instruction fetch/memory access paths and stops execution by setting `count=1` and `atbpt=1` when counts expire or equal-watch values match. `dobplist` formats active breakpoints using `symoff` against text or data symbols.
