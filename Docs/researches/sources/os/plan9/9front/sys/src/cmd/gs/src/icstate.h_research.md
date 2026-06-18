# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/icstate.h

Defines externally visible interpreter context state.

Key points:
- `gs_context_state_s` stores current graphics state, dual memory, language level, array packing, binary object format, random state, usertime fields, superexec depth, userparams, scanner options, file-permission lock, startup argument-file flag, library path, stdio refs, dictionary/exec/operand stacks, and plugin list.
- The dictionary, execution, and operand stacks are embedded at the end to minimize offsets elsewhere.
- Declares `rand_state_initial`.
- Provides `public_st_context_state` descriptor macro implemented in `icontext.c`.

Research notes:
- This is the interpreter’s per-context state container.
- It combines VM, graphics, scanning, parameter, file, and stack state.
