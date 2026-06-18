# File Research: sources/os/plan9/9front/sys/src/cmd/pwd.c

Minimal print-working-directory command. It calls `getwd` into a 512-byte buffer, prints the path, and exits with `"getwd"` on failure.

Integration points:
- Standalone Plan 9 libc command.

Risks:
- Fixed 512-byte path buffer; very long paths fail through `getwd`.
