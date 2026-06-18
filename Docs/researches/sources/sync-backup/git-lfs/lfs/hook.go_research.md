# sources/sync-backup/git-lfs/lfs/hook.go

Purpose: manages standard Git LFS hook scripts, including install, upgrade, and uninstall behavior.

Important APIs/types/functions: hook content constants, `Hook`, `LoadHooks`, `NewStandardHook`, `Exists`, `Path`, `Install`, `write`, `Upgrade`, `Uninstall`, and `matchesCurrent`.

Control flow: `LoadHooks` constructs pre-push, post-checkout, post-commit, and post-merge hooks with current content and upgradeable historical variants. `Install` creates the hook dir and writes or upgrades based on existence and force. `Upgrade` writes only if current contents match known upgradeable content. `Uninstall` removes only matching current/upgradeable hooks. `matchesCurrent` reads up to 1024 bytes, trims/undents, and compares.

State/persistence behavior: writes executable hook files, creates directories, and removes hooks from disk.

Dependencies/integration: depends on config-aware `tools.MkdirAll`, file IO, tracer logging, and localized errors. Used by install/uninstall commands.

Risks/test signals: protects user hooks by refusing to overwrite/delete unknown content unless forced install writes directly. The 1024-byte read limit can misclassify very large hooks. Content matching is exact after trim/undent, so small edits prevent automatic upgrade/uninstall.
