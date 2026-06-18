# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/misc/unix/mail.c

## Purpose
Unix C wrapper for `/bin/mail` compatibility in the upas Unix port.

## Behavior
Chooses `edmail` for no arguments or reader flags such as `-m`, `-f`, `-r`, `-p`, `-e`; exits immediately for `-n`; otherwise chooses `send`. It constructs the target path from `UPASROOT` and `execv`s the selected program.

## Dependencies
External `UPASROOT`, `edmail`, `send`, Unix `execv`.

## Risks / Notes
Old K&R C style; assumes `UPASROOT` is defined by linked configuration.
