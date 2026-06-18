# File Research: sources/os/bsd/freebsd-src/sbin/hastctl/Makefile

Builds `hastctl`, the HAST control utility.

Key contents:
- Includes many source files from sibling `hastd` via `.PATH`.
- Builds control utility support for activemap, buffers, checksum, compression, protocol, metadata, nv pairs, parser/lexer, logging, and common proto/subr code.
- Links `md`, `util`, and `z`.
- Defines Capsicum, IPv4, and optional IPv6 support.
- Defines lexer flags to avoid unused input/unput code.
- Generates parser artifacts from yacc/lex inputs and cleans them.

This target shares most of the HAST library-like implementation with `hastd` but uses `hastctl.c` as the command frontend.
