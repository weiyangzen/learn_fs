# File Research: sources/virtualization/nvme-cli/completions/bash-nvme-completion.sh

This Bash completion script registers completion for the `nvme` CLI. It is a static dispatcher around `_nvme_subcmds`, top-level command lists, vendor plugin subcommands, and per-command option tables.

Core behavior:
- `nvme_list_opts()` maps built-in nvme subcommands to supported option completions.
- Each `plugin_*_opts()` function provides option completions for a vendor or feature plugin, including Intel, WDC, Micron, Seagate, Solidigm, OCP, ZNS, and others.
- `_nvme_subcmds()` initializes completion state, declares associative arrays for plugin subcommands and option handler functions, lists top-level nvme commands, dispatches plugin completion when the second word is a plugin, and otherwise calls `nvme_list_opts`.
- It completes `/dev/nvme*` positional device arguments after a threshold number of non-option words.
- It ends with `complete -o default -F _nvme_subcmds nvme`.

Important details:
- The file mirrors many CLI options by hand, so it can drift from command definitions.
- Some option spellings appear inconsistent or typo-prone, such as `opts=+=`, missing `=` on some long options, and command-name mismatches like `changed-alloc-ns-list-log` versus `changed-alloc-cns-list-log`.
- It supports NVMe-oF commands such as `discover`, `connect-all`, `connect`, `disconnect`, `disconnect-all`, and `dim`.
- It also supports broad NVMe admin, I/O, log, namespace, security, register, telemetry, ZNS, FDP, and plugin workflows.

Integration role:
- User-facing shell ergonomics only; no runtime library logic.
- Depends on Bash completion helpers such as `_init_completion` from bash-completion.
