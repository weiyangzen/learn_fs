# File Research: sources/os/bsd/dragonflybsd/sys/sys/reg.h

Machine-independent wrapper for process register access interfaces.

Key responsibilities:
- Includes machine-specific register structure definitions from `machine/reg.h`.
- Declares kernel APIs to fill and set general registers, floating-point registers, and debug registers for an LWP.
- Declares `exec_setregs()` for setting initial register state on exec.

Important behavior:
- Provides a stable MI include path for code that manipulates architecture-specific `struct reg`, `struct fpreg`, and `struct dbreg`.

Dependencies:
- Kernel declarations use `struct lwp` and `struct proc`.

Notable risks:
- Actual structure layouts are machine-dependent; callers must not assume cross-architecture register layouts from this header alone.
