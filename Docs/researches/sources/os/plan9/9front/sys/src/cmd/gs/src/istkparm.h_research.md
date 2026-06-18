# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/istkparm.h

Defines `struct ref_stack_params_s`, the mostly immutable configuration attached to a ref stack. Fields cover bottom and top guard counts, total block size, usable data size, guard value, underflow and overflow error codes, and whether expansion is allowed.

Also provides `private_st_ref_stack_params`, a simple GC descriptor macro used by `istack.c`.
