# File Research: sources/os/plan9/9front/sys/src/cmd/git/rebase

Script that prints the commands needed to replay commits from a source branch onto a destination. It finds the common ancestor, refuses no-op rebases, logs commits in range, and emits `git/branch` plus `git/export | git/import` commands.

It does not execute the rebase directly. With `-n`, generated imports include no-commit mode. Temporary branch `rebase.wip` is used in the emitted command sequence and removed at the end.
