# File Research: sources/os/plan9/9front/sys/src/cmd/fax/receiverc

## Purpose
Post-processing rc script for received faxes.

## Key Elements
Binds the fax queue from the file server, expects `time Y|N pages [ftsi]`, special-cases likely New York Times faxes based on sender, page count, day, and hour, copies those pages to `/n/fs/lib/nyt`, removes originals, otherwise mails recipients from `faxrecipients` with a command to view pages.

## Dependencies
Uses Plan 9 rc, `9fs`, `bind`, `date`, `sed`, `seq`, `cp`, `rm`, and `mail`.

## Behavior/Risks
Hard-coded local policy and paths dominate behavior. It removes `/srv/fs` and rebinds `/mail/faxqueue`, so it is site-specific and assumes the file server namespace is available.
