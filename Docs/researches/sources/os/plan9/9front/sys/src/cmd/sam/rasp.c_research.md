# File Research: sources/os/plan9/9front/sys/src/cmd/sam/rasp.c

`rasp.c` maintains the host-side model of which file ranges the terminal knows. A rasp is a list of spans; the high bit marks spans resident in the terminal.

`raspload`, `raspstart`, `raspdone`, and `raspflush` bracket edit batches, coalesce grow/cut messages, emit `Hcheck0`, and use `outflush` for protocol flow control.

`raspdelete` updates dot/mark/cmd point positions, coalesces shrink notifications, sends `Hcut` when needed, and removes ranges from the rasp. `raspinsert` updates dot/mark/cmd point positions, grows the rasp, and either sends `Hgrow` or `Hgrowdata` depending on size and whether the insertion lands in terminal-known text.

`rcut`, `rgrow`, `rterm`, and `rdata` are low-level span-list operations. They split, merge, mark, and query terminal-known ranges while preserving the total file-length mapping.

This file is central to sam's lazy screen data protocol: the terminal can render known spans immediately and request missing spans later.
