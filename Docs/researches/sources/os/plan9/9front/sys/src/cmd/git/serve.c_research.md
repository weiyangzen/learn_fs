# File Research: sources/os/plan9/9front/sys/src/cmd/git/serve.c

Server-side upload-pack and receive-pack implementation. It advertises refs with HEAD symref and no-thin capability, negotiates wants/haves for fetch, and writes packs. For push, it validates requested ref updates, receives and verifies a pack, indexes and installs it, locks the repo, checks old refs still match, validates new hashes are commits, updates/deletes refs, and may initialize HEAD to the newest pushed ref for an empty repo.

`main` reads the initial service command pkt-line, optionally binds a path prefix, binds the requested repo at `/`, initializes git state, and dispatches `git-receive-pack` only when `-w` permits writes, otherwise `git-upload-pack`.
