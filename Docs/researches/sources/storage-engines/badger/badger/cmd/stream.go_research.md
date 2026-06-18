# sources/storage-engines/badger/badger/cmd/stream.go

Purpose: implements `badger stream`, which streams an input DB either into a new DB with selected options or into a backup file.

Important flow: flags configure output directory, output file, compression type, version retention, read-only input, and encryption key file. `stream` opens the input DB managed at `math.MaxUint64`, validates compression, and if `--out` is set checks that the target directory is absent or empty before calling `inDB.StreamDB(outOpt)`. If `--out` is absent and an output file is set, it calls `stream.Backup(f, 0)`.

State and persistence: may create a new output DB or a backup file; input is read-only by default. Dependencies are Badger streaming, options compression enum, file/directory checks, and `getKey`. Risks: the flag registration for `outFile` uses an empty long name with shorthand `f`, which is unusual; backup file is opened without truncating existing content; no explicit error is returned if neither output target is set. Test signals should include stream-to-empty-dir, non-empty-dir rejection, compression validation, encrypted DB streaming, and backup-file truncation expectations.
