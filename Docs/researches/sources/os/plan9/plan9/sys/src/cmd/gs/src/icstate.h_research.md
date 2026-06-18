# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/icstate.h

Defines externally visible interpreter context state.

`gs_context_state_s` contains:
- graphics state pointer
- dual VM memory
- language level and interpreter mode refs
- random/usertime/superexec state
- userparams and scanner/security flags
- library path and stdio refs
- dictionary, execution, and operand stacks
- plugin list

Also defines the public GC descriptor macro for context states. The stacks are deliberately placed at the end to minimize offsets elsewhere.
