# File Research: sources/os/bsd/openbsd-src/sbin/unwind/parse.y

`parse.y` is the yacc grammar and lexer for `unwind.conf`. It parses includes, macros, resolver preference order, forwarders, DoT authentication names, block-list configuration, and forced resolver rules.

The grammar builds a `struct uw_conf` with defaults of DoT, oDoT forwarder, plain forwarder, recursor, oDoT autoconf, autoconf, and stub/ASR. `preference` entries are checked for uniqueness and enable their resolver types. `forwarder` entries require numeric IP addresses, validate ports, default to port 853 for DoT and 53 otherwise, and only allow `authentication name` with DoT. `block list` can be configured once, optionally with logging. `force [accept bogus] <resolver> { domains... }` normalizes domains to trailing dots, stores them in an RB tree, and enables the forced resolver type.

The lexer supports quoted strings, comments, line continuations, numeric tokens, keywords, and `$macro` expansion with START/DONE markers to prevent recursive expansion during insertion. Included files are managed as a stack with per-file line/error accounting. `parse_config()` accepts a missing default config as a valid empty config, frees nonpersistent macros after parsing, and discards the config on accumulated errors.

Safety details: `check_file_secrecy()` rejects secret files not owned by root/current user or writable by group/world-readable or writable by others; `host_ip()` uses `AI_NUMERICHOST`, so configured forwarders do not trigger name resolution; token buffers and destination fields are bounds-checked with explicit errors.
