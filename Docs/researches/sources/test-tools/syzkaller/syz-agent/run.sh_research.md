# sources/test-tools/syzkaller/syz-agent/run.sh

Purpose: container entrypoint wrapper for syz-agent.

Important APIs/types/functions: shell script checking `GIT_COOKIE_DAEMON`.

Control flow: if enabled, starts `git-cookie-authdaemon` in background as user `syzkaller` with HOME set, then `exec`s `/app/syz-agent -syzkaller=/syzkaller "$@"` as foreground process.

State and persistence: credential daemon writes under `/home/syzkaller/.git-credential-cache`; syz-agent uses mounted workdir.

Dependencies and integration points: copied into the Docker image and invoked by Dockerfile entrypoint; controlled by prod overlay env var.

Risks: script assumes `GIT_COOKIE_DAEMON` is set; with `set -u` absent, unset compares as empty only in this script form. Background daemon failures are not supervised.

Test signals: container startup logs and ability to fetch authenticated repos.
