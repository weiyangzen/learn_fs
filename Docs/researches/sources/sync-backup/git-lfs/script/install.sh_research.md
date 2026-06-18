# sources/sync-backup/git-lfs/script/install.sh

Purpose: installs Git LFS binaries from the script directory into a chosen prefix and runs `git lfs install`.

Important behavior: prefix selection from `PREFIX`, `BOXEN_HOME`, default `/usr/local`, or `--local` for `$HOME/.local`; write-permission check; `install` of every `git*` file in the script directory.

Control flow: parse options, validate prefix writability, create `$prefix/bin`, remove existing `git-lfs*`, install matching binaries, append prefix bin to `PATH`, and run `git lfs install`.

State/persistence behavior: modifies the chosen bin directory, removes old Git LFS binaries there, and updates the user's global/system Git LFS filter configuration through `git lfs install`.

Dependencies/integration: distributed installer entrypoint for packaged Git LFS archives.

Risks: broad `rm -rf "$prefix/bin/git-lfs*"` can remove all matching files in prefix. The glob `git*` depends on script directory contents. Requires write permission and a functional Git.

Test signals: installed `git-lfs` on PATH and successful `git lfs install`.
