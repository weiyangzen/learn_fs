# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/vf/vf.c

Read fully: 1127 lines, 20307 bytes. SHA-256 prefix: `4c9d3f6db2c74e2e`.

`upas/vf` is a MIME attachment filter. It reads a message, recursively parses MIME parts, classifies content types and filenames using `/sys/lib/mimetype`, rejects or rewrites suspect executable attachments, and preserves/pass-throughs safe message content.

The parser builds `Part` objects with header lines, disposition, transfer encoding, content type, charset, boundary, filename, and temporary-buffer state. `part()` handles multipart recursion, forwarded `message/rfc822`, and leaf bodies. `passbody()` streams until an ancestor boundary, supporting temporary saved bodies when an external checker is run.

For suspect content, `problemchild()` optionally runs `/mail/lib/validateattachment`; if not accepted and not in reject-only mode, it wraps the attachment in a new multipart message explaining that headers were changed, renames the file with `.suspect`, and changes type/disposition to safer values. Hard-reject class files call `refuse()`.

Header parsing handles `Content-Type`, `Content-Transfer-Encoding`, `Content-Disposition`, boundary/name/charset/filename attributes, and RFC2047-like filename conversion for UTF-8, US-ASCII, and ISO-8859-1 with base64 or quoted decoding.

Integration: used as a mail filter before final delivery. It logs to `vf`/`mail`, can save rejected content to `-s savefile`, and signals refusal by posting a note to its process group.

Risk notes: the source contains visible debug `fprint(2, "x\n")`/similar traces in `problemchild()`. MIME parsing is hand-written and boundary-sensitive; malformed headers or unusual encodings may pass through or be wrapped conservatively.
