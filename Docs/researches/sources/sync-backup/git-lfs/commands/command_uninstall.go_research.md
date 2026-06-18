<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_uninstall.go -->
# sources/sync-backup/git-lfs/commands/command_uninstall.go

Purpose: implements `git lfs uninstall` and `git lfs uninstall hooks`, removing Git LFS filter configuration and repository hooks.

Important APIs/types/functions: `uninstallCommand`, `uninstallHooksCommand`, shared install-scope globals from `command_install.go`, `cmdInstallOptions().Uninstall`, and `uninstallHooks`.

Control flow: builds filter options using the same scope parsing as install, uninstalls config while warning on errors, optionally removes repository hooks when in repo or local/worktree scope and not skipped, then prints scope-specific removal messages.

State and persistence behavior: removes Git config entries from selected scope and uninstalls Git LFS hook snippets/files from the repository hook directory.

Dependencies/integration points: shares flag variables and option validation with install, depends on `lfs.FilterOptions`, Git version worktree support, and hook uninstall logic in `commands.go`.

Risks and test signals: risks include shared mutable install globals, warnings not always causing nonzero exit, and no global removal message for local/worktree scopes. Test signals include global/system/local/worktree/file uninstall, skip-repo, hooks-only uninstall, non-repo behavior, and hook removal errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_uninstall.go -->
