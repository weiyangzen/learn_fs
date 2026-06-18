# File Research: sources/os/plan9/9front/sys/src/cmd/upas/vf/vf.c

`upas/vf` is a MIME attachment filter. It parses multipart and forwarded-message structures, reads content headers, classifies content type and filename against `/sys/lib/mimetype`, rejects or wraps suspicious executable attachments, optionally saves rejected mail, and can delegate deeper inspection to `/mail/lib/validateattachment`.

The parser recursively handles boundaries, content type/disposition/encoding headers, RFC 2047 filename tokens, base64 and quoted-printable metadata, latin1-to-UTF conversion, Unix `From ` headers, and temporary diversion files. Dangerous attachments may be wrapped in a new multipart message with explanatory text and renamed `.suspect`; class `r` filenames are refused.

Flags select reject-only behavior and savefile. The filter is a defensive transformation stage intended to prevent automatic execution while preserving suspicious content when configured.
