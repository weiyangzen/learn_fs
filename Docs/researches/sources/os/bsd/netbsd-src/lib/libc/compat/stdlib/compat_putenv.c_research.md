# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/stdlib/compat_putenv.c

Read completely: 83 lines.

This implements legacy `putenv` behavior that copies the supplied string instead of adopting caller-owned storage. It validates the environment variable name with `__envvarnamelen`, duplicates the string, replaces `=` with NUL, calls `setenv(copy, copy + name_len + 1, 1)`, then frees the temporary copy.

Important interactions: uses current environment helpers and `setenv` while preserving older ownership semantics.

Security/reliability notes: rejects empty/invalid variable names with `EINVAL`. Since it copies before calling `setenv`, caller mutation after return does not affect the environment.
