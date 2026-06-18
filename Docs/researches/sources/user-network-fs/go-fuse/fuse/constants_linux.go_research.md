## sources/user-network-fs/go-fuse/fuse/constants_linux.go

Purpose: Linux-specific syscall open flag aliases.

Important APIs/types/functions: assigns `syscall_O_LARGEFILE` and `syscall_O_NOATIME` from `syscall`.

Control flow: compile-time build selection.

State and persistence: none.

Dependencies and integration: used by debug printing and protocol flag handling.

Risks and test signals: low-risk wrapper; regressions show up as incorrect flag formatting or behavior in Linux open-path tests.
