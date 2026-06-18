# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_os2.h

Read status: complete.

Purpose: OS/2 printer/spool helper declarations.

Contents:
- Declares `pm_find_queue`, which lists queues, finds the default queue, or resolves a supplied queue to a driver.
- Declares `pm_spool`, which spools a file to a queue or validates a queue when filename is `NULL`.

Filesystem/storage relevance:
- Header for OS/2 printer file-device support.
