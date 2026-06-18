## sources/security-integrity/attr/libmisc/next_line.c

Purpose: line reader that supports long lines and strips CR/LF.

`next_line` uses a static buffer grown by `high_water_alloc`, repeatedly reads with `fgets`, trims line terminators, and returns the shared buffer. State is static and reused across calls, so it is not thread-safe and only one returned line remains valid. Dependencies are `getpagesize`, stdio, and `misc.h`. Risks include indistinguishable EOF vs allocation failure without checking stream state, static storage, and behavior on final unterminated lines. Tests are restore-file and transcript test inputs with long lines.
