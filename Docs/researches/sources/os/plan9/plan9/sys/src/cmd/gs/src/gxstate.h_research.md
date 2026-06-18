# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxstate.h

Internal Ghostscript graphics-state API header. It forward-declares opaque `gs_state` and exposes internal state memory/save-stack/client-data hooks used primarily by the interpreter.

Key contents:
- Save/memory accessors: `gs_state_memory`, `gs_state_saved`, `gs_state_swap_saved`, `gs_state_swap_memory`.
- Client-data callback types for allocation, copying, freeing, and reason-aware copying.
- `gs_state_copy_reason_t` distinguishes `gsave`, `grestore`, `gstate`, `setgstate`, `copygstate`, and `currentgstate` copy contexts.
- `gs_state_client_procs` groups client callbacks.
- `gs_state_set_client` registers client state and notes whether pattern streams are involved.
- `gs_state_client_data` and `gx_get_clip_path_id` expose stored client data and clipping path identity.

Notable dependencies:
- Includes `gscspace.h` for color-space-related graphics-state types.
- Implementations are in graphics-state source files such as `gsstate.c`.

Research notes:
- The header explicitly says these interfaces are internal and unstable between releases.
- `copy_for` takes a non-const `from` pointer by design because some clients mutate or adjust state during copy operations.
