# sources/sync-backup/git-lfs/t/t-multiple-remotes.sh

Purpose: validates LFS object download behavior when a repository has multiple remotes and checkout/reset/pull/rebase/cherry-pick operations refer to objects hosted by a remote other than the current branch's remote.

Important APIs/functions: `prepare_consumer`, `prepare_forks`, and `exec_fail_git` are local helpers layered over `setup_remote_repo`, `git remote add`, `git fetch`, `git lfs track`, `git push`, and normal Git porcelain. The key configuration knobs are `lfs.remote.searchall` and `lfs.remote.autodetect`.

Control flow: `prepare_forks` creates two bare remotes, a main consumer that pushes an LFS-tracked `a.bin` to both remotes and then only to the main remote, and a fork consumer that fetches both. The first six tests enable either autodetection or search-all and expect reset, pull, checkout, rebase, sparse-checkout add, and cherry-pick to hydrate the object successfully. The second six disable both and require the same operations to fail through `exec_fail_git`.

State/persistence behavior: remote refs and local tracking refs are the tested state. LFS object presence differs between the main and fork endpoints, so success requires the LFS transfer layer to infer the correct endpoint from Git operation metadata rather than from the checked-out branch alone.

Dependencies/integration points: requires Git 2.27 or newer for treeish metadata used by autodetection. Integrates Git remote configuration, sparse checkout, branch tracking, cherry-pick/rebase object checkout, and LFS remote endpoint selection.

Risks/test signals: regressions either accept a download from the wrong remote configuration or reject valid cross-remote operations. The tests are sensitive to Git version behavior and to fixture server path handling through `file://` URLs.
