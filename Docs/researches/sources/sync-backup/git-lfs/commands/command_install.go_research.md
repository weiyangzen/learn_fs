<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_install.go -->
# sources/sync-backup/git-lfs/commands/command_install.go

Purpose: implements `git lfs install` and `git lfs install hooks`, installing Git LFS filter configuration and repository hooks.

Important APIs/types/functions: globals `fileInstall`, `forceInstall`, `localInstall`, `worktreeInstall`, `manualInstall`, `systemInstall`, `skipSmudgeInstall`, `skipRepoInstall`; `installCommand`, `cmdInstallOptions`, and `installHooksCommand`; `lfs.FilterOptions`.

Control flow: `cmdInstallOptions` validates Git version, optionally sets up repository for local/worktree, enforces mutually exclusive install scopes, warns for non-root system install, and builds filter options. `installCommand` installs filter config, optionally delegates to hook installation, and prints initialization status. `installHooksCommand` maps install flags onto update globals and calls `updateCommand`.

State and persistence behavior: writes Git configuration in global/local/worktree/system/file scope and installs or prints hook content depending on flags. It can skip smudge filters and skip repository hook setup.

Dependencies/integration points: depends on Git version for worktree support, `lfs.FilterOptions`, `updateCommand`, `installHooks`, and shared command configuration state reused by uninstall.

Risks and test signals: risks include shared global flag state between install/update/uninstall, system install privilege warning being advisory, and `install hooks` going through update behavior. Test signals include each scope, mutually exclusive scope rejection, skip-smudge config, manual hook instructions, force overwrite, and repository hook install failure guidance.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_install.go -->
