# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/op_set_journal_size.c

## Role

Implements `-J size=<journal-size>`, resizing all OCFS2 journals.

## Parse Flow

`set_journal_size_parse_option()` requires an argument, allocates a `uint64_t`, parses the size with `tunefs_get_number()`, and stores the pointer in `op->to_private`.

## Run Flow

`set_journal_size_run()` reads and frees the stored size pointer, prompts the user, then calls `tunefs_set_journal_size()` with null feature masks/options to resize journals without changing journal feature bits.

Writes are wrapped in `tunefs_block_signals()` / `tunefs_unblock_signals()`.

## Open Flags

Declared as `TUNEFS_FLAG_RW | TUNEFS_FLAG_ALLOCATION`, because journal resizing allocates or frees filesystem space.

## Notable Risks

- The code frees `op->to_private` before prompting. That is fine because it copies the value to `new_size`, but retry/reuse of the same operation object would not have parse state afterward.
