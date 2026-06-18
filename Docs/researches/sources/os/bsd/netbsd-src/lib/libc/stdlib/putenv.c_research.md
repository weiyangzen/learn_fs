# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/putenv.c

Implements `putenv(char *str)` by inserting the caller-owned `NAME=value` string directly into `environ`. It validates the variable name with `__envvarnamelen()`, locks the environment, finds or creates the slot with `__getenvslot()`, frees an owned previous value if present, and stores `str`.

As POSIX requires for `putenv`, the string is not copied; later caller mutations can change the environment.
