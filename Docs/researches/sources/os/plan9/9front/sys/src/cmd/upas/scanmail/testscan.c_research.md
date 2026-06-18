# File Research: sources/os/plan9/9front/sys/src/cmd/upas/scanmail/testscan.c

`testscan` is an offline driver for the scanmail pattern engine. It loads the configured pattern file or a `-p` override, reads one or more messages from a file or stdin, canonicalizes them with the same `readmsg`/`convert`/`conv64` path, and reports matched actions.

It supports debug, verbose canonical body/header dumping, and an `-a` mode that controls repeated-message handling. `dumppats()` can enumerate regex and string buckets, including alternate patterns, though it is not invoked from `main`.

The file mirrors scanmail allocation wrappers and match iteration but does not queue, hold, dump, or log messages. Its value is as a regression/manual diagnostic tool for pattern parsing and matching semantics.
