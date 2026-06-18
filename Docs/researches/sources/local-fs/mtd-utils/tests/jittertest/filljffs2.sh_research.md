# File Research: sources/local-fs/mtd-utils/tests/jittertest/filljffs2.sh

## Purpose
Repeatedly copies and removes a file to create JFFS2 fill/erase activity.

## Key Elements
Infinite bash loop: `cp $1 $2`, `rm $2`, logs `df | grep mtd` to `/dev/console`, prints sleep message, and sleeps for `$3`.

## Dependencies
Requires bash, cp/rm/df/grep, console write permissions, and positional arguments.

## Behavior/Risks
No quoting or validation of arguments, infinite loop by design, and writes to `/dev/console`.
