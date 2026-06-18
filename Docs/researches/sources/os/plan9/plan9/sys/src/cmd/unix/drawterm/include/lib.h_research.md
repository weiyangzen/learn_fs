# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/lib.h

Core Plan 9 compatibility header for drawterm.

Key contents:
- Renames conflicting libc/system symbols, defines Plan 9 scalar aliases, `Rune`, `nil`, `nelem`, `USED`, UTF constants, and syscall constants.
- Defines `Lock`, `QLock`, `Qid`, `Dir`, `Waitmsg`, and Plan 9 mount/open/qid/mode constants.
- Declares rune/UTF routines, Plan 9-style formatting and print APIs, allocation helpers, string/path helpers, base encoders, floating-point helpers, locks, randomness, syscalls, network dial/listen APIs, kernel-process helpers, error-string APIs, and encryption wrappers.

Role in this group:
- This is the main portability ABI used by almost every file in the drawterm Unix tree.

Notable risks:
- Aggressive macros such as redefining `long`, `open`, `read`, `write`, `sleep`, and many libc names require strict include ordering.
- Type widths are fixed to drawterm expectations and may differ from host ABI defaults.
