# File Research: sources/os/plan9/9front/sys/src/cmd/upas/scanmail/scanmail.c

`scanmail` is an SMTP/mail queue filter that canonicalizes incoming mail, applies configured spam patterns, and either passes the message to `upas/qer`, holds it, dumps it, saves a copy, or logs matched lines. It reads pattern data from `UPASLIB/patterns`, line logs to `UPASLOG/lines`, uses `/mail/box/<user>/nospamfiltering` for per-recipient opt-out, and rewrites the queue destination when a hold rule fires.

The main flow parses flags, collects sender and recipients, builds a lower-case sender/recipient command string, calls `canon()` to prepare header/body scan buffers, evaluates `Lineoff`, `Dump`, `HoldHeader`, `Hold`, and `SaveLine` actions in priority order, then streams the original raw message onward through `qmail()`. The scanner deliberately only scans bounded canonical buffers (`Hdrsize`, `Bodysize`) while preserving the original message for delivery.

Important behaviors include `Dump` switching `tflag` so the message is not queued, optional dump/copy files with hash-plus-random filenames, sender-domain queue naming under `-h -q`, and full bypass when all recipients opt out. Notable risks are pointer mutation in `matcher()` during dump and sender temporary mutation for domain queueing; both are local but require care when changing matching code.
