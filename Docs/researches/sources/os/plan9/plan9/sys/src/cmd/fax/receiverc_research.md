# File Research: sources/os/plan9/plan9/sys/src/cmd/fax/receiverc

Plan 9 rc script run after fax reception.

Key behavior:
- Rebinds fax queue through `9fs fs` so mail actions operate as if on the file server.
- Reads recipients from `/mail/faxqueue/faxrecipients`.
- For normal received faxes, mails the reception metadata and a `page -w spool/id.*` command to recipients.
- Contains special handling for weekday or weekend New York Times faxes from a specific `FTSI`, copying pages into `/n/fs/lib/nyt` and removing spool pages.
- Falls back to mailing postmaster for unexpected argument counts.

Important implementation details:
- Arguments are expected as `time Y|N pages [ftsi]`.
- Page extension formatting handles one to three digit page numbers.

Risks and invariants:
- Hard-coded local policy for NYT fax routing and file-server paths.
- Removes `/srv/fs` before mounting the file server namespace.
