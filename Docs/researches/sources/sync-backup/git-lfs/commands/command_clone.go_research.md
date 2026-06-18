<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_clone.go -->
# sources/sync-backup/git-lfs/commands/command_clone.go

Purpose: implements deprecated `git lfs clone`, wrapping `git clone` with filters disabled and then fetching/checking out LFS objects for the cloned repository.

Important APIs/types/functions: `cloneCommand`, `postCloneSubmodules`, `cloneFlags git.CloneFlags`, `cloneSkipRepoInstall`, `git.CloneWithoutFilters`, `setupRepository`, `buildFilepathFilter`, `fetchRef`, `pull`, and `installHooks`.

Control flow: validates Git version, warns on newer Git versions, passes mirrored clone flags to Git, finds the clone directory from the final argument or URL basename, changes into it, initializes the Git LFS repository context, applies `--origin`, and either fetches LFS objects for no-checkout/bare clones or runs `pull` and recursive submodule pulls. It then installs hooks unless `--skip-repo` is set.

State and persistence behavior: creates a new repository via Git, changes process cwd temporarily, downloads LFS objects into the clone's LFS store, mutates the working tree through checkout unless bare/no-checkout, and installs repository hooks.

Dependencies/integration points: depends on Git clone flag parity, Git version behavior around submodule filter propagation, `git submodule foreach`, global include/exclude flags, and the pull/fetch command helpers.

Risks and test signals: risks include deprecated flag coverage drifting from Git, clone directory inference for unusual URLs or explicit paths, submodule pull errors after successful parent pull, and cwd restoration. Test signals include normal clone, `--bare`, `--no-checkout`, `--origin`, include/exclude filters, recursive submodules on Git >=2.9, and hook install skipping.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_clone.go -->
