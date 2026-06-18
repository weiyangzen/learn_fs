# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gpgetenv.h

Purpose: Interface contract for platform-specific environment lookup.

Key behavior: Declares `gp_getenv(const char *key, char *ptr, int *plen)`. The header documents the three-way contract: found and copied returns `0`; found but too large returns `-1` and required size; missing returns `1`, clears output when possible, and sets size to 1.

Dependencies and notes: The documented buffer size includes the terminating NUL, which is important for all implementations and callers.
