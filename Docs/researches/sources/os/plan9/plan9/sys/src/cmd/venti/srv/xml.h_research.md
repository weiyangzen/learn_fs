# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/xml.h

Purpose: Declares XML output helpers for Venti HTTP/status code.

Key behavior:
- Declares complex emitters for `AMap`, `Arena`, and `Index`.
- Declares scalar helpers for arena names, scores, sealed flags, integers, and indentation.

Dependencies:
- Used by XML-producing server modules.

Notable details:
- Header only; implementations are split across `xml.c` and other server files.
