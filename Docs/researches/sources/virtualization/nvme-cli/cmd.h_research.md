# File Research: sources/virtualization/nvme-cli/cmd.h

- Purpose: neutralizes plugin/command list macros before including command definition files.
- Key behavior: undefines and replaces `PLUGIN(n, c)` and variadic `COMMAND_LIST(args...)` with empty definitions.
- Research note: likely used as a preprocessing include to avoid emitting declarations/definitions for a specific include pass.
