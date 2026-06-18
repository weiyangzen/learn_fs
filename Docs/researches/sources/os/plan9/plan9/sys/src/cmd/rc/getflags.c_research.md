# File Research: sources/os/plan9/plan9/sys/src/cmd/rc/getflags.c

Small command-line flag parser used by rc.

Main logic:
- `getflags()` scans `argv`, recognizes flags according to a compact format string, stores presence-only flags as `flagset`, and moves argument-taking flag values to the end of `argv`.
- `scanflag()` validates a flag spec and returns its argument count.
- `reverse()` supports in-place argument rearrangement.
- `usage()` prints reason-specific errors and generated usage text from the same flag spec.
- `errc()` buffers error output through the platform `Write()` wrapper.

Flag spec syntax supports:
- single-letter flags;
- `:<n>` argument counts;
- bracketed usage labels like `[command]`.

Risk/notes:
- `flag` is indexed directly by character value and limited by `NFLAG`.
- Duplicate flags are rejected.
