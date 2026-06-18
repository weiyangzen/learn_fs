# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/pemdecode.c

Reads a PEM file or stdin, extracts the named section with `decodePEM`, and writes raw decoded bytes to stdout.

The command requires a section tag and optional file path. It reads the entire input into memory before decoding.
