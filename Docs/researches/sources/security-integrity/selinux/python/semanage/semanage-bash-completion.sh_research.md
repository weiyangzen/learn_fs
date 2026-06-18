# sources/security-integrity/selinux/python/semanage/semanage-bash-completion.sh

## Purpose
This Bash completion script provides tab completion for the `semanage` CLI. It offers subcommand names, common options, and policy-derived completions for stores, SELinux users, roles, types, modules, domains, file types, and protocol values.

## Important APIs, types, and functions
- `__contains_word()` tests whether a word is present in a list.
- `ALL_OPTS` and `MANAGED_OPTS` define shared option groups.
- `__get_all_stores()`, `__get_all_users()`, `__get_all_types()`, `__get_all_port_types()`, `__get_all_domains()`, `__get_all_node_types()`, `__get_all_file_types()`, `__get_all_roles()`, and `__get_all_modules()` query host policy state through `/etc/selinux`, `seinfo`, and `semodule`.
- `__get_*_opts()` functions return option sets by subcommand.
- `_semanage()` is the actual completion function registered by `complete -F _semanage semanage`.

## Control flow
When Bash asks for completions, `_semanage()` inspects `COMP_WORDS[1]`, the current word, and the previous word. It first handles value completions for permissive domains and module enable/disable/remove/remove arguments. It then decides whether the user is completing the subcommand, a value for a recognized option (`-S`, `-p`, `-R`, `-s`, `-f`, or `-t`), or options for the current subcommand. Results are generated with `compgen -W`.

## State and persistence behavior
The script has no persistence. It reads system policy state and command outputs at completion time. `COMPREPLY` is the only mutated shell state.

## Dependencies and integration points
It depends on Bash completion variables, `compgen`, `/etc/selinux`, `dir`, `grep`, `cut`, `seinfo`, and `semodule`. The completion vocabulary must stay aligned with the Python `semanage` parser. It currently lists the main verbs `boolean`, `dontaudit`, `export`, `fcontext`, `import`, `interface`, `login`, `module`, `node`, `permissive`, `port`, and `user`; it does not include the Python CLI's Infiniband `ibpkey` and `ibendport` subcommands.

## Risks and edge cases
- `__get_all_stores()` is defined twice.
- The function declares `local verb comps` but never assigns `verb`; branches effectively rely on `$command` and empty `$verb`.
- The `-t` completion branch checks `--types`, while the CLI uses `--type`, so long-option type completion may not trigger.
- `__get_import_opts()` and `__get_export_opts()` advertise `--f`, but the CLI uses `-f` plus `--input_file` or `--output_file`.
- `__get_boolean_opts()` includes `-off` rather than `--off`.
- Completion for protocols only suggests `tcp udp`, omitting `dccp` and `sctp` supported by `semanage port`; node `ipv4`/`ipv6` completion is not separated from port protocol completion.
- Policy queries can be slow or absent on minimal systems; stderr is suppressed for `seinfo` but not all helpers.

## Test signals
There is no dedicated completion test. Useful smoke tests would source the script in Bash, set `COMP_WORDS` and `COMP_CWORD` for representative command lines, and verify options and value completions match the Python parser.
