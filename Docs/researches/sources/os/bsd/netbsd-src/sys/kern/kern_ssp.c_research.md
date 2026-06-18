# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_ssp.c

Read completely: 85 lines.

Implements kernel stack-smashing-protector support when built with `__SSP__` or `__SSP_ALL__`.

Behavior:
- Defines the stack canary storage as `stack_chk_guard`/`__stack_chk_guard`, with weak aliases for rump kernels.
- Defines `stack_chk_fail()`/`__stack_chk_fail()` to panic with `stack overflow detected; terminated`.
- `ssp_init()` obtains random guard bytes from `cprng_fast()`, raises IPL with `splhigh()`, copies the guard array into global canary storage without making extra function calls inside the critical update, restores IPL, and prints debug guard values.
- If SSP is not enabled, `ssp_init()` is an empty function.

Notes:
- The file is intentionally small and architecture-independent.
- Security depends on calling `ssp_init()` after entropy is available, as the comment states.
