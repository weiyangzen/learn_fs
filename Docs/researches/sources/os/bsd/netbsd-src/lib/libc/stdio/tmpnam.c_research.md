# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/tmpnam.c

Implements legacy `tmpnam()`. It uses either a static `L_tmpnam` buffer or the caller buffer, formats `P_tmpdir/tmp.<counter>.XXXXXXXXXX`, increments a static counter, and passes the template to `_mktemp()`.

The function emits an unsafe-use warning recommending `mkstemp()` or `mkdtemp()`. The static counter and static buffer make this compatibility API unsuitable for robust concurrent use.
