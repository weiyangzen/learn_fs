# File Research: sources/virtualization/guestfs-tools/bash/Makefile.am

## Scope

Build/install rules for bash completion scripts.

## Behavior

- Maintains real completion scripts for `virt-alignment-scan` and `virt-win-reg`.
- Creates symlinked completion entries for many tools that share the common completion script behavior.
- Under `HAVE_BASH_COMPLETION`, installs scripts and symlinks into `$(BASH_COMPLETIONS_DIR)`.
- Copies real scripts into the build directory for out-of-tree builds.
- Cleans generated symlinks and copied scripts.

## Tests

- Runs `test-complete-in-script.sh` with environment variables listing scripts, symlinks, and commands.

## Risks And Invariants

- Symlink targets must stay consistent with tools that support common `--short-options`/`--long-options`.
- The `symlinks="$(scripts)"` assignment in `TESTS_ENVIRONMENT` appears intentional or legacy but means the test’s command list is the main coverage signal.
