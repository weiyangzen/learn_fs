# File Research: sources/os/bsd/dragonflybsd/sys/sys/procfs.h

ELF core/procfs debugger structure definitions.

Key responsibilities:
- Includes `param.h` and machine-independent register wrapper `reg.h`.
- Typedefs general and floating-point register sets for procfs/core consumers.
- Defines versioned `prstatus_t` with sizes, OS release, current signal, PID, and general register set.
- Defines register-set aliases `prgregset_t` and `prfpregset_t`.
- Defines `prpsinfo_t` with version, size, command name, and saved argument bytes.
- Defines `psaddr_t`.

Important behavior:
- Comments explicitly state these structures must not remove/reorder fields; additions go at the end with version increments.
- Current versions are both 1.
- Provides the minimum needed for GDB ELF core dump support.

Dependencies:
- Depends on `MAXCOMLEN` from `param.h` and `struct reg`/`struct fpreg` from machine register headers.

Notable risks:
- This is debugger/core-file ABI; structure changes affect old core dump readability.
- Saved argument bytes are capped at `PRARGSZ` 80.
