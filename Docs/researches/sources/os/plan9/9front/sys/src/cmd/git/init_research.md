# File Research: sources/os/plan9/9front/sys/src/cmd/git/init

Initializes a 9front git repository. It creates `.git/refs/{heads,remotes}`, `.git/fs`, `.git/objects`, an empty `.git/INDEX9`, and `.git/HEAD` pointing to `refs/heads/<branch>`, defaulting to `front`.

It writes `.git/config` with `repositoryformatversion = p9.0`, optional remote `origin` URL, and branch remote metadata. If `-u` is omitted, it derives an upstream from `git/conf 'defaults "origin".baseurl'` plus the new directory basename.
