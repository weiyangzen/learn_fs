# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_atan2f.S

i387 float `atan2f` kernel. It loads float arguments, executes `fpatan`, and stores the float result through the ABI epilogue.
