# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_veriexec.c

## Scope

- Source file read completely: `sources/os/bsd/netbsd-src/sys/kern/kern_veriexec.c`.
- Subset scope: `Docs/research_subset_a.md`.
- This file implements NetBSD Veriexec fingerprint registration, per-file verification state, mount-specific tables, strict-mode policy, and enforcement hooks.

## Purpose And Main Interfaces

- Initialization:
  - `veriexec_init`
  - `veriexec_fpops_add`
- Lookup and verification:
  - `veriexec_lookup`
  - `veriexec_verify`
  - internal `veriexec_file_verify`
- Policy hooks:
  - `veriexec_openchk`
  - `veriexec_removechk`
  - `veriexec_renamechk`
  - `veriexec_unmountchk`
  - raw device kauth callback
- Table/file management:
  - `veriexec_file_add`
  - `veriexec_file_delete`
  - `veriexec_table_delete`
  - `veriexec_purge`
  - `veriexec_convert`
  - `veriexec_dump`
  - `veriexec_flush`

## Key Data Structures

- `struct veriexec_fpops` describes one hash algorithm: name, digest length, context size, and init/update/final callbacks.
- `struct veriexec_file_entry` stores one monitored file's lock, optional filename, access type flags, status, fingerprint bytes, hash ops, and filename length.
- `struct veriexec_table_entry` stores per-mount entry count and sysctl node.
- `veriexec_hook` is the fileassoc key binding entries to vnodes.
- `veriexec_mountspecific_key` stores per-mount Veriexec table metadata.
- `veriexec_op_lock` serializes global Veriexec operations.

## Control Flow

- `veriexec_init` registers fileassoc cleanup, device/system kauth listeners, mount-specific storage, global lock, and configured SHA fingerprint algorithms.
- `veriexec_fp_calc` reads a vnode page by page through `vn_rdwr`, updates the selected hash context, and returns the digest.
- `veriexec_file_verify` checks regular files only, looks up the vnode entry, enforces strict mode for missing entries, evaluates fingerprints when needed, validates requested access type, and enforces mismatch policy according to strictness.
- Strictness levels affect behavior:
  - learning can bypass when no table is loaded.
  - IDS denies fingerprint mismatches and protects monitored files from removal.
  - IPS additionally enforces access type, blocks writes to monitored files, and blocks monitored raw writes/unmounts.
  - lockdown denies non-monitored access and broad filesystem changes.
- `veriexec_file_add` resolves a path, validates regular file and fingerprint algorithm/length, validates entry flags, optionally evaluates on load, ignores exact duplicate hardlink entries, creates mount table state as needed, and associates the entry with the vnode.
- `veriexec_openchk` verifies opened files, blocks creation in lockdown, and handles write/truncate requests by denying or purging cached status.
- `veriexec_removechk` and `veriexec_renamechk` enforce monitored file deletion/rename policy and adjust stored filenames/entries.
- `veriexec_raw_cb` handles raw device writes: in lower modes it purges cached fingerprints for the mounted device; in IPS/lockdown it denies.
- Dump/convert functions serialize entries into proplib dictionaries for userland.

## Concurrency And Invariants

- Global operations take `veriexec_op_lock`; per-entry status/data uses `vfe->lock`.
- Verification may upgrade to writer when evaluation is needed, then downgrade to reader after status is established.
- Table deletion and file deletion use writer mode to coordinate with verification.
- Fileassoc cleanup calls `veriexec_file_free`.
- Mount-specific destructor frees sysctl nodes and table metadata.

## Risks And Edge Cases

- Raw disk write handling documents a race where fingerprints can be cached again while raw writes are possible.
- `VERIEXEC_RW_UPGRADE` busy-loops until upgrade succeeds.
- `veriexec_file_verify` returns with `vfe->lock` held on successful found entries; callers must release it.
- Filename retention is optional; dump skips entries without stored filenames.
- The active hash algorithm list depends on compile-time `VERIFIED_EXEC_FP_SHA*` options.
