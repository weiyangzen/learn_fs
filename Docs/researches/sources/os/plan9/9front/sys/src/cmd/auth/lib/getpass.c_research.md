# File Research: sources/os/plan9/9front/sys/src/cmd/auth/lib/getpass.c

Password prompt and key-derivation helper.

Key responsibilities:
- Prompts for a password with echo disabled.
- Optionally validates with `okpasswd`.
- Enforces `PASSWDLEN` maximum.
- Optionally prompts for confirmation and retries on mismatch.
- Derives an `Authkey` with `passtokey` and/or copies the plaintext password to caller buffer.
- Clears temporary password buffers before returning or retrying.

Dependencies:
- Uses `readcons`, `okpasswd`, `passtokey`, and shared `error`.

Notable risks:
- If caller asks for plaintext output, the caller owns later clearing.
