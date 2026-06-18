# File Research: sources/os/bsd/dragonflybsd/sys/sys/checkpoint.h

Public checkpoint syscall/control header with small kernel helper structures.

Key responsibilities:
- Defines checkpoint operation constants: freeze, thaw, freeze-by-pid, and thaw-binary, with the latter two noted unsupported.
- Includes procfs status/fpregset/process-info types for kernel checkpoint state capture.
- Defines `pstate_t` and `lc_args_t` for kernel thread/process state collection.
- Declares userland `sys_checkpoint()` when not compiling kernel code.

Dependencies:
- Includes `sys/procfs.h`.

Notable risks:
- The public operation constants expose unfinished modes.
- Checkpoint state depends on procfs register/status structures, tying checkpoint ABI to process inspection data layout.
