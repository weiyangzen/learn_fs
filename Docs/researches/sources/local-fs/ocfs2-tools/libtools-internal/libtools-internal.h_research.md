# File Research: sources/local-fs/ocfs2-tools/libtools-internal/libtools-internal.h

Small private header exposing internal cross-module hooks for verbosity, interaction, and progress handling.

Declarations:
- `tools_verbosity()`
- `tools_is_interactive()`
- `tools_progress_clear()`
- `tools_progress_restore()`

Research notes:
- Public tool APIs are in headers under `include/tools-internal`; this header exposes internals needed between implementation files.
