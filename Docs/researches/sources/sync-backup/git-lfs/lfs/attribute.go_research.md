# sources/sync-backup/git-lfs/lfs/attribute.go

Purpose: installs and uninstalls Git config entries for the `filter.lfs` clean/smudge/process filter, including skip-smudge variants and upgradeable historical values.

Important APIs/types/functions: `Attribute`, `FilterOptions`, `Install`, `Uninstall`, `filterAttribute`, `skipSmudgeFilterAttribute`, `normalizeKey`, `set`, and `shouldReset`.

Control flow: `FilterOptions.Install` chooses normal or skip-smudge attributes. `Attribute.Install` iterates desired properties, normalizes keys, reads the current value from local/worktree/system/file/global scope, and sets it if forced, empty, or upgradeable. Otherwise mismatched existing values produce errors. Uninstall removes the whole `filter.lfs` section from the selected scope and verifies no properties remain in `FilterOptions.Uninstall`.

State/persistence behavior: writes Git config in the chosen scope and can remove config sections. This directly changes repository/user/system filter behavior.

Dependencies/integration: depends on `git.Configuration`, localized errors, and command install/uninstall flows.

Risks/test signals: system/worktree/file writes can be destructive if scoped incorrectly. Iteration over map properties is unordered, so partial configuration is possible if a later key fails. Upgradeable values are explicit and must be maintained as command syntax changes.
