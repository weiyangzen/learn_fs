<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/doc/install/Android/git-annex-install -->
# sources/sync-backup/git-annex/doc/install/Android/git-annex-install

Purpose: convenience installer intended to be sourced in a Termux shell on Android, installing the appropriate git-annex standalone tarball and updating the current shell `PATH`.

Important control flow: maps `uname -m` to standalone architecture names (`arm64-ancient`, `armel`, `amd64`, `i386`), builds a download URL under `https://downloads.kitenet.net/git-annex/linux/current/`, installs Termux dependencies with `pkg install git wget tar coreutils proot`, downloads and extracts the tarball in `$HOME`, runs `git-annex.linux/git-annex version` to let `runshell` finish adaptation, calls `termux-setup-storage`, and appends the extracted directory to `PATH`.

State and persistence: writes/extracts `~/git-annex.linux`, installs Termux packages, may trigger storage permission setup, and mutates the current shell's `PATH` because it is meant to be sourced.

Dependencies and integration points: Termux `pkg`, `wget`, `tar`, `proot`, Android architecture naming, and the standalone bundle's Android-aware `runshell`.

Risks: piping `wget -O-` directly to `tar zx` has no checksum verification. The `x86_32` case is probably not a common `uname -m` value. Re-running can overlay an existing extracted tree. Because it should be sourced, executing it in a subshell loses the final `PATH` change.

Test signals: test architecture mapping under Termux, dependency install behavior, extraction of the correct tarball, `git-annex version` success, and immediate command availability after sourcing.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/doc/install/Android/git-annex-install -->
