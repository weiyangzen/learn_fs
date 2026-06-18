# File Research: sources/local-fs/xfsdump/inventory/getopt.h

This header provides a smaller getopt command string for inventory-related tooling.

Key content:
- `GETOPT_CMDSTRING` is `"gwrqdL:u:l:s:t:v:m:f:i"`.
- Defines option constants for dump destination, level, subtree, verbosity, dump label, media label, resume, and inventory print.
- Comments document which subsystem owns each option.

Notable mismatch:
- The command string includes letters such as `g`, `w`, `r`, `q`, `d`, `u`, `t`, and `m`, but this header only defines a subset of symbolic constants.
- It defines `GETOPT_MEDIALABEL` as `'M'`, but the command string shown here contains lowercase `m`, not uppercase `M`. This may reflect legacy/test usage or drift from the main dump getopt header.

Role:
- Used by inventory-specific code/tests rather than the main dump command parser.
