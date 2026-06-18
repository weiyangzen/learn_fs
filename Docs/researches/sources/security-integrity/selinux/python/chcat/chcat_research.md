<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/chcat/chcat -->
# sources/security-integrity/selinux/python/chcat/chcat

## Purpose
Modifies or lists MLS/MCS categories on files or SELinux login mappings.

## Important APIs, Types, And Functions
Key functions are `verify_users()`, `chcat_user_add()`, `chcat_add()`, `chcat_user_remove()`, `chcat_remove()`, `chcat_user_replace()`, `chcat_replace()`, `check_replace()`, `isSensitivity()`, `expandCats()`, `translate()`, `usage()`, `listcats()`, `listusercats()`, and `error()`. It uses Python `selinux`, `seobject.loginRecords`, `pwd`, `subprocess.check_call`, `chcon`, and `semanage login`.

## Control Flow
Startup requires MLS and SELinux enabled. Options choose delete, list, or login mode. Listing either prints translations from `selinux_translations_path()` or user categories from `getseuserbyname()`. Delete resets targets to `s0`. Otherwise the first positional argument is parsed as comma-separated categories. Pure category lists replace the range; `+cat` and `-cat` forms add/remove one category at a time. File operations use `chcon -l`; login operations inspect current semanage login records and run `semanage login -a` or `-m`.

## State And Persistence
File mode changes filesystem labels via `chcon`. Login mode persists semanage login range changes. Listing is read-only.

## Dependencies And Integration Points
It bridges human-readable category translations, raw SELinux ranges, file labels, and semanage login mappings.

## Risks And Edge Cases
`isSensitivity()` assumes nonempty strings. `expandCats()` only expands ranges when <=25 results. Add/remove paths handle only the first category in `newcat` for file operations. Subprocess failures are counted but details are suppressed.

## Test Signals
Test on MLS-enabled systems: list translations, list user categories, replace/add/remove/delete file labels, replace/add/remove login mappings, invalid users, mixed `+/-` with replacement, translated category ranges, and subprocess failure reporting.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/chcat/chcat -->
