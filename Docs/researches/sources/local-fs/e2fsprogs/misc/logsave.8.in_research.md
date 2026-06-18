# File Research: sources/local-fs/e2fsprogs/misc/logsave.8.in

## Purpose
Manpage source for `logsave`, which captures command or stdin output to a logfile while also showing it on the console.

## Key Elements
Documents `logsave [-asv] logfile cmd_prog [...]`, append mode, skip mode for control-A/control-B bracketed progress text, verbose console output, and stdin mode using `-` as the command.

## Dependencies
References `fsck(8)` and early boot logging use cases.

## Behavior/Risks
Explains deferred logging when the logfile directory is unavailable, making it relevant for boot sequences before `/var` is mounted.
