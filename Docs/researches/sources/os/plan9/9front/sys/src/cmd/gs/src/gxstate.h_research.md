# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxstate.h

Internal Ghostscript graphics-state API used mainly by interpreter and state-management code.

Key declarations:
- Opaque `gs_state` forward declaration.
- Accessors for graphics-state memory, saved state, saved-state swapping, and allocator swapping.
- Client-data hooks: allocate, copy, free, and reason-aware `copy_for`.
- `gs_state_copy_reason_t` distinguishes `gsave`, `grestore`, `gstate`, `setgstate`, `copygstate`, and `currentgstate` copy contexts.
- `gs_state_set_client` installs client state and notes whether client data owns pattern streams.
- `gs_state_client_data` accessor is declared unless overridden by `gzstate.h`.
- `gx_get_clip_path_id` exposes the current clip path identifier.

Dependencies:
- Includes `gscspace.h` for graphics/color state context and common Ghostscript types.

Research notes:
- The comments explicitly mark this as unstable internal API, not a public embedding contract.
- The non-const `from` argument in `copy_for` is deliberate for clients that mutate or lazily normalize copied data.
