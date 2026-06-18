# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh1/pubkey.c

SSH1 host public-key file parser and updater.

Key responsibilities:
- Parses SSH1 public-key records in decimal or hex forms, with optional host aliases.
- Searches keyring files for matching host aliases.
- Detects key match, missing key, missing key file, or wrong key.
- Appends or replaces host key entries.

Important functions:
- `readpublickey`, `parsepubkey`: parse public key lines.
- `match`: compare comma-separated host alias lists.
- `findkey`: lookup host key.
- `appendkey`, `replacekey`: update keyring files.

Risks/quirks:
- `parsepubkey` temporarily mutates input line while parsing.
- `replacekey` rewrites through `<keyfile>.new`, removes old file, then renames by `dirwstat`.
