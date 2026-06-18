# File Research: sources/virtualization/guestfs-tools/gnulib/lib/getprogname.h

Compatibility header for `getprogname`.

Behavior:
- If `HAVE_GETPROGNAME` is not defined, provides inline `getprogname()` returning `program_invocation_short_name`.

Research relevance: gives common code a stable program-name API for usage and diagnostics.
