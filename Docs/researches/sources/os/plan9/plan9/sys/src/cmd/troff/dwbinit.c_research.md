# File Research: sources/os/plan9/plan9/sys/src/cmd/troff/dwbinit.c

DWB pathname initialization helper used by troff and related document tools.

Key responsibilities:
- Finds the DWB home directory through `DWBhome()`.
- Reads a simple config file for `DWBENV=...`, falling back to an environment variable and then compiled default.
- Rewrites configured pointer paths and fixed-size array paths to be rooted under the current DWB home.
- Provides optional debug dumps through `DWBDEBUG=ON`.
- Provides `DWBprefix()` to replace a leading DWB prefix token in an already stored path.

Important behavior:
- The config parser is intentionally simple and only recognizes variable assignments at the first non-space token.
- Pointer path entries are newly allocated; array entries must have enough room or the program exits.
- Double leading slashes in the home path are collapsed by advancing the returned pointer.

Notable risks:
- `DWBhome()` may return malloc-owned, environment-owned, or static strings depending on path source.
- `DWBinit()` does not free old pointer values when replacing them.
- Absolute paths are still rewritten; debug only warns about them.
