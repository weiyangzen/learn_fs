## sources/test-tools/xfstests/common/parent

Purpose: this XFS helper validates parent pointer records reported by `xfs_io parent`, including positive and negative checks around hardlinks, renames, and moves.

Important APIs: `_xfs_parse_parent_pointer parents pino name` parses colon-separated parent pointer records in `inode/generation/name_length/name` shape and exports parsed values in `PPINO`, `PPGEN`, `PPNAME_LEN`, and `PPNAME`. `_xfs_verify_parent parent_path parent_pointer_name child_path` checks filesystem objects, retrieves parent pointers for a child, validates the matching record, checks that the name resolves to the same inode as the child, and verifies path printing via `parent -p`. `_xfs_verify_no_parent parent_name pino child_path` asserts that no matching parent pointer exists.

Control flow: positive verification first checks existence of the parent directory, child file, and parent/name path. It obtains parent and child inodes with `stat`, queries `xfs_io -x -c "parent -s -i ... -n ..."`, parses the output, compares inodes, then iterates paths returned by `parent -p` and checks each with `test -ef`. Negative verification returns success when `xfs_io parent` fails or parsing cannot find the matching record.

State and persistence: no persistent state is created. The parser intentionally sets global shell variables for callers and diagnostic output. All checks operate below `$SCRATCH_MNT`.

Dependencies and integration: it requires `common/rc`, `$SCRATCH_MNT`, `$XFS_IO_PROG`, `stat`, and tests that have verified XFS parent pointer support. It integrates with golden output by printing `*** ... OK` and `*** Verified parent pointer` status lines.

Risks: array assignment `parents=($(...))` and unquoted path tests make spaces or special characters in test names unsafe. Error diagnostics include a likely typo `$PPPINO` instead of `$pppino`. `_xfs_parse_parent_pointer` reads from `echo "$parents"`, so records containing shell word splits can be damaged.

Test signals: successful positive checks end with `*** Parent pointer OK for child ...`; failures print missing objects, missing parent pointer records, bad name length, mismatched inode resolution, or bad path printing. Negative checks are silent unless a forbidden record is found.
