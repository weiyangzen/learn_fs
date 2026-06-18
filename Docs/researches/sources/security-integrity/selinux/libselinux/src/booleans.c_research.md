# sources/security-integrity/selinux/libselinux/src/booleans.c

Purpose: `booleans.c` implements SELinux boolean discovery, reading pending/active values, setting pending values, and committing them through `selinuxfs`. It also supports boolean-name substitutions through `booleans.subs_dist`.

Important APIs/types/functions: exported functions include `security_get_boolean_names()`, `security_get_boolean_pending()`, `security_get_boolean_active()`, `security_set_boolean()`, `security_commit_booleans()`, `security_set_boolean_list()`, deprecated `security_load_booleans()`, and `selinux_boolean_sub()`. `bool_open()` centralizes path construction and substitution fallback.

Control flow: names are read by `scandir(selinux_mnt/booleans)` with dot entries filtered. Boolean values are read as three-byte strings where the first byte is active and second is pending. Setting validates name/value, opens the boolean file, writes `"0\0"` or `"1\0"`, and commit writes to `/commit_pending_bools`. List setting applies each value then commits, rolling back earlier booleans to active values on set failure.

State and persistence: changes are persisted only after `security_commit_booleans()`. Pending writes live in kernel SELinux boolean state. The disabled build path compiles stubs returning `-1`.

Dependencies and integration: depends on `selinux_mnt`, path helpers, kernel `selinuxfs` boolean files, and `SELboolean` public API.

Risks and test signals: names with `/` are rejected to prevent path traversal. Rollback can itself fail silently. Permanent flag deliberately returns error after commit because it is no longer used. Tests should cover substitutions, ENOENT, disabled build stubs, active/pending parsing, list rollback, and commit failure.
