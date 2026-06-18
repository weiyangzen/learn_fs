# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipmon/ipmon_y.y

`ipmon_y.y` is the IPMon configuration grammar and action engine.

Grammar coverage:
- `match { ...; } do { ...; }` rules.
- Variable assignments with `set_variable()`.
- Dynamic action loading through `load_action <name> <path>`.
- Match predicates: direction, destination/source IPv4 CIDR, destination/source port, rate limits by seconds or packets, group, interface, protocol, result, rule, logtag, nattag, and log type (`ipf`, `nat`, `state`).
- Action list entries call named saver backends, optionally with one string argument.

Implementation model:
- Parses match options into temporary `opt_t` lists, then builds `ipmon_action_t`.
- Detects duplicate match comparator use within one rule using `macflags`.
- Maintains a global action list and saver list.
- Built-in savers are registered by `ipmon.c`; dynamic savers are loaded with `dlopen()` and required symbols named `<name>destroy`, `<name>parse`, `<name>print`, and `<name>store`, with optional `<name>dup` and `<name>match`.
- `check_action()` evaluates parsed actions against an IPF log record and formatted message, enforcing direction/type/every/dst/src/ports/group/interface/protocol/result/rule/logtag/nattag predicates, then invokes each matched saver callback.
- `load_config()` installs lexer keyword table, opens the config file, and repeatedly runs `yyparse()`.
- `unload_config()` destroys actions and unloads dynamically loaded saver modules.
- `dump_config()` and `print_action()` reconstruct configured rules for diagnostics.

Notable issues:
- The grammar sets `a->ac_rule = o->o_num`, but the rule parser assigns `o_num = YY_NUMBER` rather than `$3`; that appears to store the token code instead of the configured rule number.
- `type` printing compares `ac_type` against `IPL_LOGIPF`/`IPL_LOGSTATE`/`IPL_LOGNAT`, while parsing stores magic constants (`IPL_MAGIC`, `IPL_MAGIC_NAT`, `IPL_MAGIC_STATE`), so dump output may not match parsed type values.
