# File Research: sources/teaching/minix/minix/fs/Makefile.inc

## Purpose

Common include for MINIX filesystem service Makefiles.

## Build Role

Sets default install directory `BINDIR?=/service`, disables manual pages with `MAN?=`, and includes the parent `Makefile.inc`.

## Dependencies

Depends on the higher-level MINIX make include one directory above.

## Risks

Small policy file. Changes affect all filesystem services that include it, especially installation location.
