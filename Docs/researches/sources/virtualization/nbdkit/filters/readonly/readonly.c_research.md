# File Research: sources/virtualization/nbdkit/filters/readonly/readonly.c

This filter forces permanent or file-controlled read-only behavior. Without `readonly-file`, `.open` forces the underlying plugin to open readonly and `.can_write` returns false. With `readonly-file=FILENAME`, the backend is opened normally, `.can_write` delegates, and mutating requests are rejected whenever the file is readable at request time.

`is_readonly_mode` centralizes rejection for pwrite, trim, and zero, logging the operation and returning `EROFS`. Flush is intentionally not blocked because writes issued before read-only mode may still need to be persisted.

This design supports dynamic read-only toggling by creating/removing the configured file. The tradeoff is that advertised write capability can remain true while individual write-like requests later fail with `EROFS`.
