# File Research: sources/os/bsd/freebsd-src/sbin/hastd/Makefile

Builds the `hastd` daemon.

Key contents:
- Builds daemon sources for activemap, control, ebuf, event, checksum, compression, protocol, hooks, metadata, nv, secondary, primary, parser/lexer, socket protocols, rangelock, and common helpers.
- Installs `hastd.8` and `hast.conf.5`.
- Defines Capsicum, default TCP port 8457, IPv4, and optional IPv6 support.
- Links `geom`, `md`, `pthread`, `util`, and `z`.
- Generates and cleans yacc/lex artifacts.

This is the full HAST runtime target, including primary/secondary worker roles and network protocol support.
