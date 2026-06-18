# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/misc/unix/makefile

## Purpose
Unix makefile for building/installing the mail wrapper and notification/vacation utilities.

## Behavior
Builds `mail` and `notify`, generates `sed.file` substitutions for `LIBDIR` and `HOSTNAME`, installs `gone.fishing`, `gone.msg`, `/bin/mail`, and optional compiled binaries, then provides cleanup targets.

## Dependencies
Unix `make`, C compiler, upas config object, shell tools, `/usr/lib/upas`.

## Risks / Notes
Install targets perform privileged copies/chown/chmod and assume legacy filesystem layout.
