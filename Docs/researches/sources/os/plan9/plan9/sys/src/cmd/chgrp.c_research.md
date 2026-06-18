# File Research: sources/os/plan9/plan9/sys/src/cmd/chgrp.c

Implements Plan 9 `chgrp`. It parses `-u` and `-o` as aliases for changing `uid` instead of `gid`, then calls `dirwstat` on each file with only the requested owner/group field set in a `nulldir`.

Behavior is intentionally small: `argv[0]` is the new group/user, remaining args are targets. Failures are printed per file and the process exits with `"can't wstat"` if any failed.
