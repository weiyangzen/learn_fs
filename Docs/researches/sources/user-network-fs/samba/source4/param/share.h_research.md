# sources/user-network-fs/samba/source4/param/share.h

Purpose: `share.h` defines the share configuration abstraction used by Samba4 NTVFS and related services.

Important APIs, types, and functions: It declares `struct share_context`, `struct share_config`, `enum share_info_type`, `struct share_info`, `struct share_ops`, public share APIs, option name macros, and default values.

Control flow: Backends implement `share_ops` to initialize contexts, retrieve typed options, list shares, fetch configs, and optionally create/set/remove shares. Generic callers use wrapper functions from `share.c`.

State and persistence behavior: `share_context` stores selected ops and backend private data. `share_config` names a share and carries backend opaque service data. Persistent state is backend-defined.

Dependencies and integration points: It forward declares `loadparm_context` and `tevent_context`; the classic backend maps these options to loadparm service parameters. POSIX/simple NTVFS backends use macros such as `SHARE_PATH`, `SHARE_READONLY`, and mask defaults.

Risks: Defaults are security-sensitive: `SHARE_READONLY_DEFAULT` is true, create mask is 0744, and directory mask is 0755. Option names must remain stable because backend code and smb.conf compatibility rely on them.

Test signals: Tests should verify each typed accessor, option defaults, classic mapping, and behavior for optional mutation functions on read-only backends.
