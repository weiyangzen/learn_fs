<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/sftp/config.go -->
# sources/sync-backup/restic/internal/backend/sftp/config.go

## Purpose
Parses and registers SFTP backend repository locations.

## Important APIs, Types, And Functions
Config, NewConfig, init, and ParseConfig are important.

## Control Flow
ParseConfig supports sftp://user@host[:port]/directory and sftp:user@host:directory forms, handles IPv6 URL form, splits user@domain@host, cleans paths, and rejects tilde-leading paths.

## State And Persistence Behavior
Config holds connection/subprocess parameters; no persistence here.

## Dependencies And Integration Points
Depends on net/url, path, strings, internal/errors/options.

## Risks And Edge Cases
Ambiguous colon/@ parsing is handled carefully; tilde rejection avoids server-dependent expansion surprises.

## Test Signals
config_test.go covers common, IPv6, absolute, relative, and invalid forms.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/sftp/config.go -->
