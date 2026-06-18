# sources/user-network-fs/rclone/cmd/obscure/obscure.go

Purpose: implements `rclone obscure`, transforming a plaintext password into rclone’s obscured config representation.

Important API: Cobra `commandDefinition`; it delegates to `obscure.MustObscure` and prints the result. It accepts exactly one password argument, or `-` to read the first line from stdin when stdin is piped.

Control flow: `RunE` validates args, checks `os.Stdin.Stat` for non-terminal input when arg is `-`, scans one line with `bufio.Scanner`, then obscures and prints inside `cmd.Run`. If no stdin is available, `-` is obscured literally. The long help explicitly says this is not secure encryption.

State/persistence: no file or remote mutation; stdout output only. Dependencies are `fs/config/obscure` and Cobra. Risks include shell history exposure of passwords and users misunderstanding obscuring as secure encryption. Test signals likely exist in config/obscure package, not this wrapper.
