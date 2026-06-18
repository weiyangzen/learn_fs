# sources/security-integrity/selinux/libsemanage/src/debug.h

Purpose: internal debug and status helper header for libsemanage implementation files.

Important APIs/types/functions: defines status constants `STATUS_SUCCESS`, `STATUS_ERR`, and `STATUS_NODATA`; macro `msg_write`; convenience macros `ERR`, `INFO`, and `WARN`; and declarations for default and relay handlers.

Control flow: implementation files call `ERR(handle, ...)` and related macros. The macro stores message metadata on the handle, invokes the configured callback, and restores `errno` afterward.

State and persistence behavior: affects only handle message fields and callbacks; no store persistence.

Dependencies and integration points: includes public debug API, libsepol debug, errno, stdio, and internal handle layout. Used broadly by parser, database, and direct API code.

Risks: macros require a valid internal handle pointer and use `__FUNCTION__`. Test signals are preserved `errno`, correct metadata, and no callback call when suppressed.
