# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/fenv.c

x86 fenv implementation covering x87 and optional SSE/MXCSR state. A constructor probes `machdep.sse` and captures the runtime x87 control word for `__fe_dfl_env`.

Functions synchronize exception flags, masks, rounding modes, and environment save/restore across x87 and SSE when available. Extension routines expose exception enable/disable state.
