# File Research: sources/os/bsd/netbsd-src/lib/libintl/textdomain.c

Implements gettext domain binding state.

Key behavior:
- Initializes default binding for domain `messages` at `/usr/share/locale`.
- `textdomain` gets/sets current default domain, with empty string resetting to default.
- `bindtextdomain` creates or updates a per-domain locale path and invalidates the current mapping.
- `bind_textdomain_codeset` stores a per-domain output codeset.
- Domain bindings are kept in a simple linked list headed by `__bindings`.

This file owns `__current_domainname`.
