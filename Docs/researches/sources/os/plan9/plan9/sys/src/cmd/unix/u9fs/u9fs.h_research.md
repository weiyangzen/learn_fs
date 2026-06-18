# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/u9fs.h

- Role: Shared declarations for u9fs authentication modules and server globals.
- Key content: `Auth` interface with auth/attach/init/read/write/clunk callbacks; exported auth methods; `remotehostname`, `Eauth`, `autharg`, `msize`; auth fid helpers; `randombytes`; `safecpy`.
- Integration: Included by `u9fs.c`, `random.c`, and auth modules.
- Risks/notes: `Auth` differs from older `u9fsauth.h`, reflecting the expanded auth-fid callback model.
