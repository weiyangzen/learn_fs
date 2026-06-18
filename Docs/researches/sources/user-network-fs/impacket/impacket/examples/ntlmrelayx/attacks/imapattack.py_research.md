# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/attacks/imapattack.py

## Purpose
`imapattack.py` implements the IMAP/IMAPS relay attack. It searches or dumps a mailbox and writes selected messages as `.eml` files into the configured loot directory.

## Important APIs, Types, and Functions
- `PROTOCOL_ATTACK_CLASS = "IMAPAttack"` advertises the plugin.
- `IMAPAttack(ProtocolAttack)` registers `PLUGIN_NAMES = ["IMAP", "IMAPS"]`.
- `run()` performs mailbox selection, search/dump selection, message fetch, filename sanitization, file write, and logout.

## Control Flow
`run()` selects `config.mailbox` read-only and falls back to `INBOX` if selection fails. If `dump_all` is false, it searches `SUBJECT` or `BODY` for `config.keyword` and truncates results to `dump_max` when configured. If `dump_all` is true, it builds a numeric range up to `dump_max` or mailbox count. Each selected message is fetched with `RFC822`, sanitized into a `mail_<user>-<mailbox>_<id>.eml` filename, and written to `config.lootdir`.

## State and Persistence Behavior
The attack writes email files to local loot storage and logs progress. It does not modify the mailbox because it selects read-only, and it logs out at the end.

## Dependencies and Integration Points
It depends on `re`, `os`, `impacket.LOG`, and the attack base. It assumes an IMAP client with `select`, `search`, `fetch`, and `logout` methods.

## Risks and Edge Cases
- `rawdata` handling mixes bytes/strings depending on the IMAP library, and filenames also assume text usernames.
- File writing uses text mode even though RFC822 payloads can be bytes.
- Search result splitting on `' '` can fail for byte results or unusual server responses.
- No creation of `lootdir` is performed here.

## Test Signals
Tests should fake IMAP responses for mailbox fallback, keyword search, dump-all max behavior, fetch failures, filename sanitization, bytes-vs-string payloads, and logout execution.
