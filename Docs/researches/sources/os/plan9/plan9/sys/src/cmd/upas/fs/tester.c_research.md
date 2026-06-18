# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/fs/tester.c

## Purpose
Standalone mailbox parser test utility.

## Behavior
Creates a root message, reads a mailbox file via `readmbox`, and recursively prints message/part metadata: sizes, Unix from/date, address headers, subject, filename, type, and charset.

## Dependencies
`message.h`, `String`, `newmessage`, `readmbox`, and message fields from the mailfs parser.

## Risks / Notes
Hard-coded default `./mbox`; exits success even on read error after printing `boom`.
