# File Research: sources/local-fs/e2fsprogs/misc/util.c

## Purpose
Provides helper routines shared by `tune2fs` and `mke2fs` for program-name extraction, user confirmation, mount safety checks, journal option parsing/sizing, fsck reminder output, and MMP diagnostic printing.

## Key Elements
`get_progname` strips directory prefixes from `argv[0]`. `proceed_question` prompts for confirmation, optionally auto-proceeding after a timeout via `alarm`, `setjmp`, and `longjmp`. `check_mount` rejects mounted or busy target devices unless sufficiently forced.

`parse_journal_opts` parses comma-separated `-J` options for external journal device, journal size, fast-commit size, journal location, and v1 journal superblock mode, storing results in the global variables declared by `util.h`. Invalid options print usage guidance and terminate.

`figure_journal_size` obtains default journal parameters from libext2fs and applies requested journal/fast-commit sizes, enforcing JBD2 minimum/maximum total blocks and ensuring the journal does not consume more than half the free filesystem blocks. `print_check_message` summarizes automatic fsck mount/time policy. `dump_mmp_msg` prints MMP failure details from an MMP block.

## Dependencies
Depends on libext2fs, JBD kernel structures, e2p, blkid/devname support, com_err, NLS wrappers, POSIX file/signal/time APIs, and `util.h`. Provides a fallback `strcasecmp` when the platform lacks one.

## Behavior/Risks
Several helpers terminate the process on invalid input or unsafe mount state, matching command-line utility expectations. `proceed_question` uses process-global signal/alarm state. Journal option parsing mutates shared global state used later by `tune2fs` and `mke2fs`, so ordering and single-process reuse matter.
