# File Research: sources/local-fs/exfatprogs/fsck/repair.c

`repair.c` implements the repair policy and prompting layer used by `fsck.c`. It maps problem codes from `repair.h` to prompt type, default behavior, preen eligibility, and rename menu defaults.

The core table `problems[]` classifies each repairable condition:
- boot checksum/boot region fixes.
- corrupt or unknown dentry deletion/fix cases.
- file dentry secondary count, stream/name/hash/length fixes.
- rename cases for dot names, duplicate names, and invalid names.
- file size/cluster-chain truncation cases.
- vendor GUID warning defaulting to no.
- recursive MBR required and MBR clear operations.

`ask_repair()` applies global fsck options:
- `-n` or problem default-no refuses repair.
- `-y` or default-yes accepts repair.
- interactive ask mode reads `stdin`.
- auto/preen mode accepts only problems flagged `ERF_PREEN_YES`.
- rename prompts return menu numbers rather than booleans.

`exfat_repair_ask()` prints the formatted problem description, obtains a decision, and marks `fsck->dirty` for accepted repairs. Truncation-style repairs additionally mark `fsck->dirty_fat`.

Rename repair support has two paths:
- `get_rename_from_user()` reads a new name, UTF-16 encodes it, validates exFAT filename rules, flushes pending iterator state, and rejects names already present in the parent directory.
- `generate_rename()` auto-generates `FILE%07d.CHK` names using `iter->invalid_name_num`, skipping collisions.

`exfat_repair_rename_ask()` decodes the old UTF-16 name for display, presents a three-choice menu, obtains or generates a UTF-16 replacement, updates the first name dentry, recalculates the name hash, and patches the stream dentry name length/hash. It returns `1` for repaired, `0` for declined, and negative on invalid/unrecoverable rename flow.

The file depends on directory iterator dirty access and lookup helpers from `libexfat`/`exfat_dir`, but it intentionally does not perform broader filesystem traversal itself.
