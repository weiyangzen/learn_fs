# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/u9fsauth.h

- Role: Older/smaller authentication interface header.
- Content: Defines `Auth` with only `session` and `attach` callbacks.
- Integration: Not referenced by the read u9fs makefile object list’s main server path; likely retained for older auth code compatibility.
- Risks/notes: Conflicts structurally with `u9fs.h` if included together.
