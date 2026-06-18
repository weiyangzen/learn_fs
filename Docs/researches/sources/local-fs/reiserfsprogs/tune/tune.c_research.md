# File Research: sources/local-fs/reiserfsprogs/tune/tune.c

Main implementation of `reiserfstune`, the ReiserFS tuning utility. It modifies journal parameters/location, converts non-standard journals, updates v3.6 UUID/label/check metadata, and stores bad-block lists.

Major responsibilities:
- Prints messages and usage.
- Parses long/short options for journals, UUID/label, bad blocks, force, check intervals, mount counts, and version/help.
- Determines when non-standard journal settings can be converted to standard layout.
- Writes standard journal parameters and journal header through `set_standard_journal_params()`.
- Zeroes journal blocks in `zero_journal()`.
- Parses integer/time/check options.
- Adds or replaces bad-block lists through `add_badblocks()`.
- Validates mounted/dirty/journal state before writes.
- Edits v3.6 superblock UUID, label, max mount count, mount count, check interval, and last check time.
- Creates or relocates journals through `reiserfs_create_journal()`.

Important implementation details:
- `should_make_journal_standard()` checks superblock magic, requested device, journal size, max transaction size, and reserved main-device area.
- `add_badblocks()` opens the on-disk bitmap, loads user bad-block bitmap, removes already-listed blocks for append mode, marks unused bad blocks in the filesystem bitmap, and rewrites bad-block tree items.
- The tool refuses to run on mounted filesystems.
- It checks clean unmount/consistency before tuning, and also checks for non-replayed transactions in an opened old journal.
- UUID/label/check metadata is only allowed for format 3.6; format 3.5 rejects those operations.
- If no new journal device is specified and no journal-size/transaction change is requested, it prints current parameters and exits.

Dependencies and interactions:
- Uses `tune.h`, `parse_time.h`, core ReiserFS open/journal/bitmap/bad-block APIs, UUID library when configured, and shared output/confirmation helpers.
- Calls `can_we_format_it()` before using a new journal device.

Risks and notes:
- Static option state uses zero as “not specified”, so explicitly setting mount/check values to zero is not supported despite some signed checks being present.
- In the v3.6 `Mnt_count` branch, the validation mistakenly checks `Max_mnt_count <= 0` before setting mount count.
- Bad-block free-block accounting subtracts `fs_badblocks_bm->bm_set_bits` rather than the local `marked` count after filtering, which deserves scrutiny.
- Many operations are intentionally destructive and guarded by mounted/clean checks plus confirmation for journal zeroing.
