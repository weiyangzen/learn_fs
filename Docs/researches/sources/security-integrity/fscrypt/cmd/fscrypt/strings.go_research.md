# sources/security-integrity/fscrypt/cmd/fscrypt/strings.go

## Purpose
Stores CLI usage strings, help templates, argument labels, and pluralization.

## APIs, Types, and Control Flow
Defines `shortUsage`, argument label constants, text templates for app, command, and subcommand help, `plurals`, and `pluralize`. Templates use the global indent from `format.go` and `urfave/cli` template data.

## State, Dependencies, and Integration
These constants shape all help and usage output. `pluralize` is reused in errors and status text.

## Risks and Test Signals
`pluralize` assumes every non-singular word exists in `plurals`; unknown words produce empty text. Help output changes affect CLI golden output and user docs.
