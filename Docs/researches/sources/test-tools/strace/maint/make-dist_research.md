# sources/test-tools/strace/maint/make-dist

Purpose: release helper that creates a clean distribution checkout, runs bootstrap/configure/distcheck, performs release checks, and exports source artifacts.

Important APIs/types/functions: resolves commit id, computes parallel make jobs from `getconf`, clones the local `.git` with `git clone -n -s`, runs `git checkout`, `build-aux/git-set-file-times`, `bootstrap`, `configure --enable-maintainer-mode`, `make distcheck`, optional `make news-check`, `make-dsc`, and copies `strace.spec` and tarballs.

Control flow: create a temp dist directory named with the shell PID, install cleanup trap, clone and checkout requested commit, prepare autotools tree, run distribution checks, skip news check if commit is not exactly tagged `v*`, generate Debian source control text, copy spec and tar artifacts up one level.

State and persistence behavior: creates and deletes the dist checkout; leaves `strace.dsc`, `strace.spec`, and tarballs in the original working directory. Uses `set -x` for traceability.

Dependencies and integration points: release engineering flow; depends on Git, Autotools, make, maintainer-mode dependencies, and `make-dsc`.

Risks: cleanup trap uses unquoted variables in places and removes the temp dir on exit; failures before artifact copy leave no dist tree for inspection. Shared clone assumes local `.git` is complete.

Test signals: successful `make distcheck`, optional `news-check`, generated tarballs, Debian `.dsc`, and spec file.
