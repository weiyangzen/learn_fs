# sources/user-network-fs/rclone/cmd/reveal/reveal.go

Purpose: implements `rclone reveal`, reversing rclone’s obscured password format for inspection/debugging.

Important API: Cobra `commandDefinition`; delegates to `obscure.Reveal` and prints result.

Control flow: validates one password argument; if reveal fails, returns the error; otherwise prints plaintext to stdout.

State/persistence: no file/remote mutation, but exposes secret material on stdout. Dependencies are config obscure package and Cobra. Risks include terminal logs/shell capture leaking passwords. Tests likely live in obscure package.
