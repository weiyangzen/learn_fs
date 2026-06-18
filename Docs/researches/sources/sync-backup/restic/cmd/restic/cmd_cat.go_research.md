# sources/sync-backup/restic/cmd/restic/cmd_cat.go

Purpose: implements `restic cat`, a diagnostic command for printing raw or JSON representations of internal repository objects.

Important APIs/functions: `catAllowedCmds` defines supported object classes. `validateCatArgs` checks object type and required IDs. `runCat` opens a read lock, parses IDs where needed, and dispatches config, index, snapshot, key, masterkey, lock, pack, blob, and tree output.

Control flow/state: JSON-like objects are marshaled with indentation and printed through the terminal printer. Raw pack/blob/tree bytes are written to `term.OutputRaw`. Pack output intentionally returns bytes even if hash validation fails, while printing a warning. Blob lookup loads the index and searches data then tree blob types. Tree lookup resolves `snapshot:subfolder` before loading the tree blob.

Dependencies/integration: repository loading, snapshot lookup, key/lock loaders, restic ID parsing, and terminal raw output. It is read-only except for repository lock files.

Risks/test signals: raw output can be binary and unsuitable for terminals. `masterkey` exposes sensitive key material to stdout. Tests cover argument validation only; object loading behavior relies on repository integration/manual diagnostics.
