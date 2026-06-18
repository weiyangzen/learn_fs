# File Research: sources/os/plan9/9front/sys/src/cmd/git/push

User-facing push wrapper around `git/send`. It selects branches from `-a`, `-b`, or current branch, optional force/debug/remove/upstream flags, and remote URLs from config or direct upstream value.

For each remote it runs `git/send`, then parses status lines. Successful updates write corresponding `.git/refs/remotes/<upstream>/...` tracking refs, deletes remove tracking refs, and unchanged refs print "up to date".
