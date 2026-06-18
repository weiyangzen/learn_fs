# File Research: sources/os/bsd/netbsd-src/lib/libc/ssp/ssp_redirect.c

Read completely: 56 lines.

This file forces definitions of selected SSP redirect functions into libc by compiling with `_FORTIFY_SOURCE 2` and `__ssp_inline`. A static `__used` function references fortified forms of `getcwd`, `read`, and `readlink` through harmless calls.

Important interactions: ensures redirect symbols required by fortified headers are emitted in libc.

Security/reliability notes: runtime use is not intended; its value is link-time symbol materialization.
