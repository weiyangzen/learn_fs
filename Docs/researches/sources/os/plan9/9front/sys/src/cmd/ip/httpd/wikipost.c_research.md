# File Research: sources/os/plan9/9front/sys/src/cmd/ip/httpd/wikipost.c

POST-only magic helper for wiki edits. It parses form fields including title, version, text, service, comment, author, and base URL; decodes URL escaping with a Latin-1 fallback heuristic; removes carriage returns; and rejects dangerous service/title/comment inputs.

It mounts a private or `/srv/wiki.<service>` wiki filesystem at `/mnt/wiki`, writes the edit record to `/mnt/wiki/new`, commits with a zero-length write, reads the resulting page name, and returns a `303 See Other` redirect to the new index or error page.
