# sources/test-tools/xfstests-bld/fstests-bld/get-all

Purpose: `get-all` clones and pins the external repositories needed by fstests-bld according to configured repository URLs and optional commit variables.

Important APIs, types, and functions: functions `have_commit()`, `checkout_commit()`, and `setup_repo()`. CLI supports `-n`/`--no-action`. Required repos include fio, libaio, quota, xfsprogs-dev, xfstests-dev, fsverity, and blktests. Optional repos include ima-evm-utils, keyutils, stress-ng, util-linux, syzkaller, nvme-cli, and ltp-dev.

Control flow: loads `config.custom` if present else `config`, parses no-action mode, then calls `setup_repo()` for each repo. `setup_repo()` removes a plain directory where a git repo is expected, clones missing repos, handles absent optional URLs, and checks out configured commits. `checkout_commit()` refuses to proceed with uncommitted changes, updates remote origin URL if needed, fetches missing commits, validates commit existence, and checks out the target commit unless in no-action mode.

State and persistence: creates, removes, fetches, and checks out git working trees under the fstests-bld directory. It can change remote origin URLs. In normal mode it mutates repository state; in no-action mode it prints intended actions and uses non-destructive checks where possible.

Dependencies and integration points: depends on config variables named `<REPO>_GIT` and `<REPO>_COMMIT`. It is a prerequisite for build scripts that require pinned external source trees.

Risks: `rm -rf "$repo_name"` for plain directories is destructive by design. `git status -s >& /dev/null` suppresses output but still requires a valid repo. Commit checkout refuses dirty trees, which protects user work but can block automation. Optional repo removal from config while directory exists is treated as an error.

Test signals: run `./get-all --no-action` with representative configs; test missing required URL, optional absent URL, dirty repo refusal, changed remote URL, missing commit fetch, and plain-directory replacement in a scratch tree.
