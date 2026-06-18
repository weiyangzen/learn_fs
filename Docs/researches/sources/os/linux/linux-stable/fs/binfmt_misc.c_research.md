# File Research: sources/os/linux/linux-stable/fs/binfmt_misc.c

## Summary
Implements Linux `binfmt_misc`: a user-namespace-aware pseudo-filesystem and binary-format loader that matches executables by extension or magic bytes and runs a registered interpreter/wrapper.

## Main Responsibilities
- Registers the `binfmt_misc` filesystem and `linux_binfmt` handler.
- Maintains per-user-namespace handler lists, falling back to ancestor namespaces.
- Parses register strings of the form `:name:type:offset:magic:mask:interpreter:flags`.
- Exposes `/status`, `/register`, and per-entry files.
- Enables, disables, or deletes one handler or all handlers through file writes.
- Rewrites `linux_binprm` argv/interpreter state for matched binaries.
- Supports special flags: preserve argv0, open binary, credentials, and pre-open interpreter file.

## Important Behavior
`load_misc_binary()` finds the active namespace handler, rejects inaccessible script paths, optionally preserves argv0, pushes the target binary path and interpreter onto the argument stack, changes `bprm->interp`, opens or clones the interpreter file, and sets `execfd_creds` for credential-preserving handlers.

`create_entry()` validates and decodes registration input. Magic handlers parse an offset, hex-escaped magic, optional mask, and reject matches beyond `BINPRM_BUF_SIZE`. Extension handlers match the suffix after the last dot in `bprm->interp`.

The filesystem instance is lazily allocated per user namespace in `bm_fill_super()`. `load_binfmt_misc()` walks from current user namespace to ancestors, using release/acquire ordering with `bm_fill_super()` so child namespaces without their own mount can use parent handlers.

Handler lifetime is protected by `entries_lock`, the root inode lock for structural updates, dentries for pseudo-files, and a `users` refcount so removal can race safely with `load_misc_binary()`.

## Risks
Registration parsing is delimiter-sensitive and accepts escaped binary bytes, so bounds checks around `MAX_REGISTER_LENGTH`, decoded magic length, and buffer padding are critical. `MISC_FMT_OPEN_FILE` pins an interpreter file and must close it exactly once. Removal relies on list deletion plus recursive dentry removal plus inode eviction, so refcount ownership must remain balanced.
