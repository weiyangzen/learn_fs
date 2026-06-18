# File Research: sources/os/plan9/9front/sys/src/cmd/auth/pemdecode.c

PEM section decoder.

Key responsibilities:
- Reads all input from a file or stdin.
- Extracts a named PEM section with `decodePEM`.
- Writes decoded binary to stdout.
- Fails on missing section, read, or write errors.

Dependencies:
- Uses libsec PEM/base64 support.
