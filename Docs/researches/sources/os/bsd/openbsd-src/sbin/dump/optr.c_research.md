# File Research: sources/os/bsd/openbsd-src/sbin/dump/optr.c

## Purpose
Operator interaction, status reporting, fstab scanning, and “what needs dumping” reporting for `dump`.

## Key Behavior
- `query()` prompts on `/dev/tty`, repeats prompts via alarms, accepts yes/no answers, and adjusts dump timing to exclude operator wait time.
- `alarmcatch()` reprints or broadcasts attention requests every two minutes.
- `interrupt()` asks whether to abort on SIGINT.
- `broadcast()` invokes `wall -g operator` when notification is enabled.
- `timeest()` reports estimated completion every five minutes once enough blocks have been written.
- `msg()` and `msgtail()` format dump diagnostics and maintain `lastmsg` for broadcasts.
- `quit()` emits an error and aborts the dump.
- `getfstab()` collects dumpable FFS/UFS fstab entries.
- `fstabsearch()` matches by mountpoint, block device, raw device, DUID, and paths without leading slash.
- `lastdump()` implements `dump -w` and `dump -W`, sorting dumpdates and comparing against fstab frequencies.
- `datesort()` sorts by filesystem name and descending dump date.

## Notes
This file is the human recovery interface for a tool that may require tape changes or decisions after write/read failures.
