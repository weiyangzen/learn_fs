# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gpgetenv.h

Purpose: Declares the platform-specific `gp_getenv` routine and documents its buffer-size contract.

Key interface: `int gp_getenv(const char *key, char *ptr, int *plen)`.

Behavior: Missing keys return 1, write an empty string when possible, and set required length to 1. Present keys return 0 if the value plus terminator fits, or -1 with the required size if it does not fit.

Dependencies: Included by platform and miscellaneous code that needs consistent environment lookup semantics.

Risks and notes: Callers must treat `*plen` as buffer capacity on input and required/actual storage size on output, including the terminating NUL.
