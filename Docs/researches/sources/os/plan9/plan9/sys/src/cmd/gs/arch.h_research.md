# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/arch.h

This is the Ghostscript architecture-selection shim for Plan 9 builds. It includes `386.h`, `mips.h`, `alpha.h`, `arm.h`, or `amd64.h` based on architecture macros such as `T386`, `Tmips`, `Talpha`, `Tarm`, and `Tamd64`.

If no known architecture macro is set, it intentionally emits invalid text telling the maintainer to update `arch.h`.

Notable observation: the `Tpower` branch includes `"mips.h"` rather than `"power.h"`, which looks suspicious given that a `power.h` file exists elsewhere in the directory.
