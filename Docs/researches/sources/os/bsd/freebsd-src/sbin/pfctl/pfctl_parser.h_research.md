# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/pfctl_parser.h

## Purpose
Shared public header for pfctl parser, optimizer, table, ALTQ, address, rule, and display helpers.

## Main Elements
- Defines option bits such as `PF_OPT_VERBOSE`, `PF_OPT_NOACTION`, `PF_OPT_NUMERIC`, `PF_OPT_NODNS`, and parser/load category flags.
- Declares `struct pfctl`, including device/libpfctl handles, anchor stacks, table transaction state, ethernet anchor state, limit trees, and `set` option state.
- Defines parser node structures for interfaces, hosts, MACs, OS fingerprints, queue bandwidth/service curves, table initializers, optimizer tables, and optimizer rule containers.
- Declares rule append, ALTQ, pool, limit, config, table, fingerprint, interface, host, and print helper APIs.
- Provides FreeBSD compatibility aliases mapping `SIMPLEQ_*` to `STAILQ_*`.

## Dependencies And Integration
Included across pfctl sources and test builds. It bridges parser-generated structures, libpfctl handles, PF kernel ABI structures, ALTQ queue structures, and radix/table buffer APIs.

## Risk Notes
This header is a broad coupling point. Struct layout and macro changes can break parser, optimizer, table loading, and display code simultaneously.
