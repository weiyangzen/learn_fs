<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_change_password.go -->
# sources/sync-backup/kopia/cli/command_repository_change_password.go

Purpose: implements `repository change-password`, changing the repository format password and updating local password persistence.

Important APIs/types/functions: `commandRepositoryChangePassword`, `askForChangedRepositoryPassword`, `repo.DirectRepositoryWriter`, `rep.FormatManager().ChangePassword`, and `passwordPersistenceStrategy().PersistPassword`.

Control flow: setup registers `--new-password` with an environment variable override and direct repository write action. `run` obtains the new password from flag or interactive prompt, calls the format manager password-change API, logs success, and persists the new password for the repository config.

State/persistence behavior: mutates the repository format password and local password store. Existing clients with cached old credentials may fail after the change, especially with format blob cache disabled.

Dependencies/integration: depends on format version support for password changes, direct repository access, password prompting, and password persistence backend. Risks/test signals: failure after repository password change but before local persistence could leave repository updated while local convenience credentials remain stale.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_change_password.go -->
