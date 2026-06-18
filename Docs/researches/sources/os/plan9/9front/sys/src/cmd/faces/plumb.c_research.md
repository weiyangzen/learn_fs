# File Research: sources/os/plan9/9front/sys/src/cmd/faces/plumb.c

## Purpose
Connects `faces` to Plan 9 plumbing and converts mail notifications into `Face` records.

## Key Elements
Opens `send` and `seemail` ports, stores watched maildirs, sends `showmail` plumb messages, parses plumb attributes, normalizes sender names into user/domain, parses multiple mail date formats, receives new/delete/modify notifications, and can synthesize faces from upas/fs mailbox `info` files for initial loading.

## Dependencies
Uses libplumb, Plan 9 time parsing (`tmparse`, `tzload`), mailbox info file layout, and shared functions from `faces.h`.

## Behavior/Risks
Duplicate detection uses mail digest when present. `setname` lowercases the sender buffer in place and supports both `user@domain` and `domain!user`; simple unqualified senders may leave domain unset for default-domain lookup.
