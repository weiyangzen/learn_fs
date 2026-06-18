# File Research: sources/os/plan9/9front/sys/src/cmd/atazz/tabs.h

Command and feature tables for `atazz`.

Important contents:
- Register name aliases for ATA FIS fields.
- SMART feature/register tables, SCT action tables, feature-control tables, error-recovery timer tables, write-same tables, and general log page names.
- Human-readable SCT error strings and ATA/SATA feature names.
- Large `atatab` array mapping ATA command codes to flags, packet flags, protocol, optional feature table, formatter, and command name.

This file is mostly declarative metadata consumed by the parser and issuer in `main.c`.
