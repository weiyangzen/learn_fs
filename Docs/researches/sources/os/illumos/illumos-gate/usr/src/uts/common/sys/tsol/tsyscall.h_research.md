# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tsol/tsyscall.h

## Purpose
Trusted Extensions syscall subcommand number definitions.

## Main Interfaces
- Defines `TSOL_SYSLABELING`, `TSOL_TNRH`, `TSOL_TNRHTP`, `TSOL_TNMLP`, `TSOL_GETLABEL`, and `TSOL_FGETLABEL`.

## Dependencies And Relationships
Used by the Trusted Extensions syscall dispatcher and user/kernel request routing for label and trusted-network database operations.

## Research Notes
This is a command-number header only; argument structures live in other TSOL headers and syscall implementation files.
