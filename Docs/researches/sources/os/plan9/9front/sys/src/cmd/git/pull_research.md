# File Research: sources/os/plan9/9front/sys/src/cmd/git/pull

Fetch-and-fast-forward script. `update` discovers local heads/remotes, runs `git/get`, and rewrites remote `refs/heads` or `refs/tags` advertisements into `.git/refs/remotes/<upstream>/...`.

After fetch, unless `-f` fetch-only is used, it compares local `HEAD`, remote branch, and their LCA. It exits cleanly if up to date, reports divergence with suggested `git/merge`, or fast-forwards the local branch with `git/branch -mnb`. `-q` suppresses log summary; `-d` enables debug fetch.
