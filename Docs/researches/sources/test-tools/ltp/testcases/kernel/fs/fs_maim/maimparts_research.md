# sources/test-tools/ltp/testcases/kernel/fs/fs_maim/maimparts

Purpose: destructive Perl orchestrator that repartitions a target disk into three partitions, runs mount/fsck cycling on each, and then runs the backup simulation.

Important APIs/types/functions: `sfdisk -g`, generated `/tmp/part.cfg`, `sfdisk --force`, `$parts`, `$fstype`, `partbeat`, `backbeat`, and Perl arrays for partition names.

Control flow: reads target disk name, iteration count, and filesystem type, queries disk geometry, divides cylinders by three, writes an sfdisk config, force-applies it to `/dev/$target`, runs `partbeat` for each partition, then calls `backbeat` using the three partition devices.

State/persistence behavior: rewrites the target disk partition table and creates `/tmp/part.cfg`. This is intentionally destructive and can remove all data from the specified disk.

Dependencies/integration: coordinates `partbeat` and `backbeat` helpers in the same directory. Depends on root privileges, `/sbin/sfdisk`, working block devices, filesystem tools, and mount permissions.

Risks/test signals: the prologue warning is accurate: passing the wrong device destroys data. Geometry parsing is fragile and assumes old sfdisk output. Test signals are printed helper output and nonzero helper failures, though the script itself does not consistently check every command status.
