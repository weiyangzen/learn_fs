# sources/user-network-fs/rclone/cmd/rcat/rcat.go

Purpose: implements `rclone rcat`, streaming stdin into a remote object.

Important APIs/state: package global `size`; Cobra command with `--size` hint; delegates to `operations.RcatSize`.

Control flow: validates one destination file path, refuses terminal stdin, splits destination Fs and remote leaf, then reads from `os.Stdin` and uploads via `operations.RcatSize(context.Background(), fdst, dstFileName, os.Stdin, size, time.Now(), nil)` in a command run context.

State/persistence: consumes stdin and creates/replaces a remote object. Dependencies include cmd parsing and operations Rcat/transfer implementation. Risks include unbounded stdin, interrupted uploads that cannot always retry, incorrect `--size` causing backend failures, and destination overwrite. Test signal is likely in operations rcat tests.
