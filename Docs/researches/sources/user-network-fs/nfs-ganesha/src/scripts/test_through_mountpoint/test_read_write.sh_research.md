<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/test_through_mountpoint/test_read_write.sh -->
# sources/user-network-fs/nfs-ganesha/src/scripts/test_through_mountpoint/test_read_write.sh

## Purpose
This script verifies basic read/write fidelity through a mounted export by copying a generated reference file into the export and back, first with `cp` and then with `cp -p`.

## Important APIs, Types, and Functions
It accepts `REPERTOIRE` as the mountpoint directory, builds a date-stamped `FICH_TEST`, and uses `TEMOIN=/tmp/TEST_RW.$DATE`. The content source is `COMMANDE_CONTENU="find /etc -ls"`. It uses `cp`, `cp -p`, `ls -l`, `diff`, and `rm`.

## Control Flow
The script validates that the argument is a directory, writes `find /etc -ls` output to the local reference file, copies it into the mount, compares source and mounted copy, copies the mounted file back to `/tmp`, compares again, removes the mounted file, repeats the same flow with `cp -p`, then removes all test files.

## State and Persistence Behavior
It writes one temporary local file and one mounted-export file named with the current day/month/year. Because the filename granularity is one day, concurrent or repeated runs on the same day can collide. There is no trap-based cleanup on failure.

## Dependencies and Integration Points
It depends on Bash-style `[[ ]]`, `/etc` being readable enough for `find /etc -ls`, local `/tmp`, and core utilities. It exercises NFS-Ganesha write, read, metadata preservation, and remove paths.

## Risks and Test Signals
Risks include unquoted paths, date-based filename collisions, no explicit exit-on-error despite `diff` failures, and environmental noise from changing `/etc` traversal output before the reference is created. Test signals are zero `diff` output/status for both normal and preserved copies and matching size/metadata expectations after `cp -p`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/test_through_mountpoint/test_read_write.sh -->
