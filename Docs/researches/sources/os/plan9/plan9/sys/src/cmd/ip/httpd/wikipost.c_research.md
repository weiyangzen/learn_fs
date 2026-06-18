# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/wikipost.c

POST-only magic helper for wiki edits. It reads form data, decodes URL escapes with a Latin-1 fallback heuristic, removes carriage returns, and extracts title, version, text, service, comment, author, and base URL fields.

It validates required fields and dangerous service/title/comment content, caps text size, mounts a private or `/srv/wiki.<service>` wiki filesystem at `/mnt/wiki`, writes an edit record to `/mnt/wiki/new`, commits with a zero-length write, reads the resulting page name, and returns a `303 See Other` redirect.
