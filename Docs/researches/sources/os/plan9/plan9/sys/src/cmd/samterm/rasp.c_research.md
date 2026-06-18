# File Research: sources/os/plan9/plan9/sys/src/cmd/samterm/rasp.c

Implements the terminal-side rasp, a linked list of known text sections and holes.

Key functions:
- `rinit` and `rclear` initialize/free a rasp.
- `rsinsert`, `rsdelete`, `splitsect`, and `findsect` manage `Section` boundaries.
- `rresize` applies host grow/cut operations.
- `rdata` stores received rune data into a hole.
- `rclean` coalesces adjacent compatible sections.
- `rload` loads available text into `scratch` and reports rune count.
- `rmissing` and `rcontig` find missing or contiguous spans for host requests.

Behavior notes:
- `Section.text == nil` marks text the terminal knows exists but has not loaded.
- Data sections allocate `TBLOCKSIZE+1` runes so text is NUL-terminated for frame use.
- `findsect` can split sections to align operations exactly on requested offsets.
