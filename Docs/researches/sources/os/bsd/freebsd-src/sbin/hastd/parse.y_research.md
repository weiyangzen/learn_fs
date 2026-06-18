# File Research: sources/os/bsd/freebsd-src/sbin/hastd/parse.y

Read completely: 1037 lines.

This yacc grammar parses HAST daemon configuration files and resolves global, node-level, resource-level, and resource-node-level settings into a `struct hastd_config`.

Key responsibilities:
- Parses directives for control socket, pidfile, listen addresses, replication mode, checksum, compression, timeout, exec hook, metaflush, node blocks, and resource blocks.
- Matches `on <node>` sections against hostname, short hostname, `kern.hostuuid`, and `hostid<kern.hostid>`.
- Applies defaults: control address, pidfile, IPv4/IPv6 listen addresses, memsync replication, no checksum, hole compression, default timeout, no exec hook, and metaflush enabled.
- Validates positive timeout, string lengths, duplicate resource names, required remote/local configuration, and presence of a matching node section per resource.
- Fills per-resource provider name, local path, remote/source addresses, replication/checksum/compression/timeout/exec/metaflush, role state, file descriptors, ggate unit, and protocol version.
- Synthesizes default listen addresses only for address families supported by the kernel.

Important interactions:
- Consumed by `hastd.c` at startup and reload.
- Uses tokenization state from the generated lexer via `yyin`, `yytext`, `depth`, and `lineno`.
- Uses `hast.h` constants for roles, replication, checksum, compression, addresses, and defaults.

Reliability and security notes:
- Host identity matching is central: only sections for the current node affect local configuration.
- `remote none` is accepted as the literal string `"none"`, later treated by primary code as no real remote.
- Config reload reparses through this same path, so parse failures leave the previous live config active.
- Memory cleanup is explicit in `yy_config_free()`, including both temporary default listen entries and accepted config lists.
