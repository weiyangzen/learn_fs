# sources/user-network-fs/rclone/cmd/md5sum/md5sum.go

Purpose: implements `rclone md5sum` as a dedicated wrapper around hashsum behavior with fixed `hash.MD5`.

Important APIs: Cobra `commandDefinition`; shared flags from `hashsum.AddHashsumFlags`; `hashsum.CreateFromStdinArg`, `GetHashsumOutput`, and globals; operations `CheckSum` and `HashLister`.

Control flow: accepts zero or one remote path, first allowing stdin hashing if no arg or `-` with piped data. For remote mode it creates a source Fs and either validates against `--checkfile` or lists MD5 hashes, optionally with `--download`, `--base64`, and `--output-file`.

State/persistence: can read stdin, create/truncate output files, and read checksum files. No remote mutation. Risks mirror `hashsum`: package-global shared flag state and output-file overwrite. Test signal likely comes from hashsum/operations and command integration.
