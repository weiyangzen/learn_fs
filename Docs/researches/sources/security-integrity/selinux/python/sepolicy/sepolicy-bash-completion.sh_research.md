# sources/security-integrity/selinux/python/sepolicy/sepolicy-bash-completion.sh

## Purpose
This bash completion script provides dynamic completions for the `sepolicy` CLI. It completes subcommands, common options, SELinux domains, booleans, classes, users, port types, policy paths, and filesystem paths using installed SELinux query tools and sepolgen interface metadata.

## Important Functions
Helper functions include `__contains_word`, `__get_all_paths`, `__get_all_ftypes`, `__get_all_networks`, `__get_all_booleans`, `__get_all_types`, `__get_all_admin_interfaces`, `__get_all_user_role_interfaces`, `__get_all_user_domains`, `__get_all_users`, `__get_all_classes`, `__get_all_port_types`, `__get_all_domain_types`, and `__get_all_domains`.

`_sepolicy()` is the completion dispatcher. It determines the current verb from `COMP_WORDS`, offers top-level verbs and common options, then branches for `booleans`, `communicate`, `generate`, `interface`, `manpage`, `network`, and `transition`. It uses `COMPREPLY`, `compgen`, and `compopt -o filenames` for file/directory completions. The script registers `complete -F _sepolicy sepolicy`.

## Control Flow
At completion time, `_sepolicy` inspects `COMP_WORDS[1]`, current and previous words, and scans for a recognized verb not treated as an option argument. Without a verb it completes verbs or policy files after `-P/--policy`. With a verb it completes option names or context-specific argument values based on `prev`.

## State And Persistence
No persistent state is written. Runtime state is shell-local variables and `COMPREPLY`. Dynamic candidate lists are read from commands and files at completion time.

## Dependencies And Integration Points
It depends on bash completion internals, `seinfo`, `getsebool`, `awk`, `sed`, `tail`, `dir`, `grep`, `cut`, `/var/lib/sepolgen/interface_info`, and the installed SELinux policy environment. It mirrors the subcommands and many options defined by `sepolicy.py`.

## Risks And Edge Cases
The option lists contain apparent typos or drift, such as `-all` rather than `--all` in some entries, duplicate `-u --list_user`, `-i --interface` while the Python parser uses `--interfaces`, and missing newer options such as `manpage --source_files`. Several helper functions parse command output with simple text filters that may be fragile across tool versions. `for w in $*` and unquoted command substitutions can split values on whitespace.

## Test Signals
No tests are present in this subset. Manual signals are successful completion for every `sepolicy.py` subcommand and no stderr noise when SELinux tools are absent or policy data is unavailable.
