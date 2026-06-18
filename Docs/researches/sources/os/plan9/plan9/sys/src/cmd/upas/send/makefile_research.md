# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/send/makefile

## Purpose
Legacy Unix makefile for building and installing `upas/send`.

## Behavior
Defines source/object lists, include paths, compile/link rules, dependencies, `prcan`, `clean`, `cyntax`, and privileged install target that copies `send` to upas lib and `/bin/rmail`, strips, chowns root, and sets setuid mode.

## Dependencies
C compiler, upas common/config/libc archives, `/usr/lib/upas`.

## Risks / Notes
Install target creates setuid-root binaries; source list includes historical modules beyond this research group.
