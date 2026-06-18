# File Research: sources/os/plan9/plan9/sys/src/cmd/cc/omachcap.c

This file provides the default machine-capability hook for the compiler.

Key behavior:
- Defines `machcap(Node*)` to always return `0`.

Important details:
- This is the default “old cc” behavior; architecture-specific compiler variants can override capability decisions elsewhere.
- It is consulted by code paths such as boolean generation/64-bit optimization decisions.

Filesystem relevance:
- Indirect compiler target hook.
