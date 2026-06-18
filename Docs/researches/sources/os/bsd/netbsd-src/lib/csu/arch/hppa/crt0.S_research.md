# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/hppa/crt0.S

HPPA process entry stub. It initializes the global offset table pointer using PC-relative code, copies it to `%r19`, then rearranges arguments for common `___start`.

`ps_strings` is moved through `%arg2`; cleanup becomes `%arg0`, and `ps_strings` becomes `%arg1` in the branch delay slot.
