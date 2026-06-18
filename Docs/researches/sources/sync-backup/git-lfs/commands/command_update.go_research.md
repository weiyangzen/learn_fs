<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_update.go -->
# sources/sync-backup/git-lfs/commands/command_update.go

Purpose: implements `git lfs update`, updating repository hooks and migrating legacy/invalid `lfs.<url>.access` config values.

Important APIs/types/functions: globals `updateForce`, `updateManual`; `updateCommand`; `regexp.MustCompile` for access keys; `getHookInstallSteps`; and `installHooks`.

Control flow: validates Git version and repository, scans all Git config keys for `lfs.<...>.access`, converts `private` to `basic`, removes invalid values, rejects simultaneous `--force` and `--manual`, then either prints manual hook install instructions or installs hooks with optional overwrite and detailed remediation on failure.

State and persistence behavior: mutates local Git config access keys and hook files. Manual mode only prints hook content after config access cleanup.

Dependencies/integration points: used directly and indirectly by install hooks, depends on hook loading/installing in `commands.go`, local config APIs, and regex key parsing.

Risks and test signals: risks include rewriting local config before hook failure, only accepting `basic` and `private`, shared globals with install, and manual/force conflict. Test signals include private-to-basic migration, invalid access removal, basic preservation, manual output, force overwrite, hook collision failure, and non-repo rejection.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_update.go -->
