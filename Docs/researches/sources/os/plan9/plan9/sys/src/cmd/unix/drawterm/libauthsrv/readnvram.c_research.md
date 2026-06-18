# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/readnvram.c

This file reads Plan 9 auth secrets from NVRAM-like storage or asks interactively.

Key behavior:
- `readnvram` searches configured platform storage paths, optional `nvram`, `nvrlen`, and `nvroff` environment overrides, and fills `Nvrsafe`.
- `check` validates checksums and zeroes bad data.
- `readcons` prompts on `/dev/cons`, optionally in raw mode for secrets.
- `finddosfile` and `dosparse` locate an NVRAM file inside DOS/FAT-style storage when offset is `-1`.

Important details:
- Built-in table covers `sparc`, `pc`, `mips`, `power`, and `debug` paths.
- If storage cannot be read or validation fails, interactive prompts collect auth id, auth domain, and password-derived key material.
- Present source is not listed in `libauthsrv/Makefile`.
