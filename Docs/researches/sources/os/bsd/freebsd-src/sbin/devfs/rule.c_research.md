# File Research: sources/os/bsd/freebsd-src/sbin/devfs/rule.c

## Purpose
Implements `devfs rule` and `devfs ruleset` subcommands by translating textual rules into devfs ioctls.

## Main Elements
- Rule command table: `add`, `apply`, `applyset`, `del`, `delset`, `show`, and `showsets`.
- `rule_main()`: parses optional `-s ruleset` and dispatches rule commands.
- `ruleset_main()`: switches active ruleset via `DEVFSIO_SUSE`.
- `rulespec_infp()` / `rulespec_instr()` / `rulespec_intok()`: parse rules from stdin, strings, or argv tokens into `struct devfs_rule`.
- Rule grammar supports optional rule number, conditions `type` and `path`, and actions `hide`, `unhide`, `user`, `group`, `mode`, and `include`.
- `rulespec_outfp()`: prints kernel rules back in parseable form.

## Dependencies And Integration
Uses devfs ioctls on `mpfd`, password/group lookups, and mode parsing via `setmode()`/`getmode()`.

## Risk Notes
Rules directly affect device visibility and permissions in a devfs mount. User/group numeric fallbacks use `eatoi()` with comments noting overflow concerns.
