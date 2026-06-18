# sources/security-integrity/fscrypt/cmd/fscrypt/format.go

## Purpose
Formats CLI help text, flag usage, and wrapped paragraphs to terminal width.

## APIs, Types, and Control Flow
Package init computes the longest flag display and terminal width capped at 120 columns, defaulting to 80. `prettyFlag` extends `cli.Flag` with display metadata. `shortDisplay` formats `--name` or `--name=ARG`. `longDisplay` aligns flag descriptions and appends defaults. `wrapText` wraps paragraphs with padding while preserving blank lines and lines beginning with `>` as code blocks.

## State, Dependencies, and Integration
Global `lineLength`, `indentLength`, `maxShortDisplay`, and `flagPaddingLength` influence all help and error wrapping. Used by command setup, error messages, and string templates.

## Risks and Test Signals
Terminal width detection happens at init, so output can vary unless tests force 80 columns through `expect` and non-terminal fallback. Wrapping changes affect golden CLI output.
