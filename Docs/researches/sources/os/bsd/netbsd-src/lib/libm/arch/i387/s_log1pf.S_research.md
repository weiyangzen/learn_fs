# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_log1pf.S

i387 float `log1pf` implementation. `_log1pf` uses the same magnitude branch as the double variant, choosing `fyl2x` or `fyl2xp1`; `log1pf` is a weak alias.
