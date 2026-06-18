# File Research: sources/os/bsd/netbsd-src/lib/libc/resolv/Makefile.inc

Build fragment for resolver sources in libc. It sets `.PATH`, defines `COMPAT__RES` and `USE_POLL`, and adds resolver files such as `h_errno.c`, `herror.c`, `res_comp.c`, `res_data.c`, `res_init.c`, `res_query.c`, `res_send.c`, `res_state.c`, and `mtctxres.c`.

It also includes `res_compat.c` specifically for `COMPAT__RES`, and suppresses a string overflow warning for `res_query.c`.
