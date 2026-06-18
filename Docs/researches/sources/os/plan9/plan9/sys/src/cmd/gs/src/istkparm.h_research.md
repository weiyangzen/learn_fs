# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/istkparm.h

Purpose: defines `ref_stack_params_t`, the mostly immutable initialization parameters for expandable ref stacks.

Fields capture bottom/top guard sizes, block size, usable data size, guard value, underflow/overflow error codes, and whether stack expansion is allowed. The file also declares the private simple GC descriptor macro used by `istack.c`.
