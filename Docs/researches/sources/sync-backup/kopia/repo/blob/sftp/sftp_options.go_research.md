# sources/sync-backup/kopia/repo/blob/sftp/sftp_options.go

Purpose: defines JSON-serializable configuration for the SFTP/SSH blob provider.

Important APIs/types/functions: `Options` includes remote `Path`, `Host`, `Port`, `Username`, password or key credentials, known-hosts file/data, external SSH command settings, embedded `sharded.Options`, and embedded `throttling.Limits`. `knownHostsFile` defaults to `$HOME/.ssh/known_hosts`.

Control flow: `sftp_storage.go` consumes these options to build either an internal SSH client or an external `ssh -s sftp` process, choose password versus public-key auth, validate absolute file paths, and construct sharded storage under `Path`.

State and persistence behavior: options can embed sensitive password/key/known-hosts data into connection info; `kopia:"sensitive"` tags mark password and key data. The remote path is the root for sharded `.f` blob files and `.shards` metadata.

Dependencies/integration: embeds sharding and throttling option structs, allowing the same provider config to influence directory layout and rate limits when higher layers wrap storage.

Risks and edge cases: relative key or known-hosts paths are rejected by storage setup. Embedded known-hosts data is later written to a temporary file because the SSH knownhosts parser accepts file paths only.

Test signals: `sftp_storage_test.go` checks absolute-path validation, embedded versus file-based credentials, password and key authentication, provider validation, and connection-info round trips.
