# sources/sync-backup/git-crypt/commands.hpp

Purpose: public interface for git-crypt command handlers and command-specific help emitters.

Important APIs/types/functions: `struct Error` carries user-facing error messages; declarations for plumbing commands `clean`, `smudge`, `diff`; public commands `init`, `unlock`, `lock`, `add_gpg_user`, `rm_gpg_user`, `ls_gpg_users`, `export_key`, `keygen`, `migrate_key`, `refresh`, `status`; matching `help_*` functions; and `get_git_config`.

Control flow: this header has no runtime flow, but it defines the command dispatch contract consumed by `git-crypt.cpp` and implemented by `commands.cpp`.

State/persistence behavior: no direct state. Declared commands manipulate Git config, key files, worktree files, and repository `.git-crypt` state in the implementation.

Dependencies/integration: includes only `<string>` and `<iosfwd>` to keep compile coupling low. It is the boundary between CLI dispatch, GPG helper access to Git config, and command implementation.

Risks/test signals: adding a command requires updating this header, `commands.cpp`, and dispatch/help in `git-crypt.cpp`. Tests should verify every declared public command is either dispatched or intentionally hidden/stubbed.
