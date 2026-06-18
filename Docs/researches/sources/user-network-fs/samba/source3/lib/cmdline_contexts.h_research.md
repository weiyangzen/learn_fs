# sources/user-network-fs/samba/source3/lib/cmdline_contexts.h

Purpose: declares command-line messaging context helpers.

Important APIs/types/functions: forward declaration of `cmdline_messaging_context(config_file)` and `cmdline_messaging_context_free()`.

Control flow: callers request a global messaging context after optional config loading and later free global state through the paired function.

State and persistence: no public state; implementation uses global Samba state.

Dependencies/integration: includes no heavy headers, relying on surrounding declarations for `struct messaging_context`.

Risks/test signals: consumers must be aware that implementation may exit in clustered/root error cases. Compile tests should verify the lightweight header can be included without pulling full messaging internals.
