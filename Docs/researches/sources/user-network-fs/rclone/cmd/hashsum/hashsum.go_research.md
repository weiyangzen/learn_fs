# sources/user-network-fs/rclone/cmd/hashsum/hashsum.go

Purpose: implements `rclone hashsum`, a generic hash listing/checking command for remote objects or stdin data. It also exposes reusable flags/helpers used by dedicated hash commands such as `md5sum` and `sha1sum`.

Important APIs: global flags `OutputBase64`, `DownloadFlag`, `HashsumOutfile`, `ChecksumFile`; `AddHashsumFlags`; `GetHashsumOutput`; `CreateFromStdinArg`; Cobra `commandDefinition`. `CreateFromStdinArg` detects omitted remote or `-` with piped stdin and delegates to `operations.HashSumStream`.

Control flow: command accepts zero to two args. Zero args print `hash.HelpString`; otherwise it parses `hash.Type`, handles stdin, creates the source Fs, and runs either `operations.CheckSum` against `--checkfile` or `operations.HashLister`, optionally writing to `--output-file`.

State/persistence: mutable package globals hold CLI flag state; output files are created/truncated with `os.Create`; stdin mode consumes process stdin. Dependencies include `cmd`, `fs/hash`, `operations`, pflag/cobra. Risks include package-global leakage in tests and overwrite behavior for output files. Test signals are indirect through md5sum/sha1sum and operations tests.
