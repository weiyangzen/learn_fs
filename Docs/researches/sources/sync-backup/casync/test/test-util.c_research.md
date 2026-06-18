# sources/sync-backup/casync/test/test-util.c

Purpose: directly tests low-level sparse write/read helpers.

Important APIs/types/functions: builds a buffer with zero and nonzero regions, writes it through `loop_write_with_holes`, checks punched byte counts, reads back with `loop_read`, tests an unaligned zero run, and verifies pipe behavior where hole punching must not occur.

Control flow/state: uses temp unlinked file and pipe fds; all assertions are local and deterministic except filesystem punch-hole support.

Dependencies/integration: covers `util.c` sparse I/O functions that archive extraction relies on for efficient sparse files.

Risks/test signals: expected punched count assumes hole punching succeeds for the temp filesystem; pipe subtest guards fallback behavior.

Source research group: `subset-b-009122`.
