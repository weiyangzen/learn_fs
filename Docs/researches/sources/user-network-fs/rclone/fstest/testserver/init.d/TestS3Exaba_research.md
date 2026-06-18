
# sources/user-network-fs/rclone/fstest/testserver/init.d/TestS3Exaba

Purpose: starts an Exaba S3-compatible server container for rclone S3 provider testing.

Important APIs/types/functions: maps API port `28635` and web UI port `28636`, sets cluster name/size, and emits provider `Exaba` config with endpoint/webui URLs.

Control flow: Docker run, then print S3 config. Access/secret strings are placeholders instructing use of the web UI.

State/persistence: disposable container with internal cluster data.

Dependencies/integration: shared Docker lifecycle and `testserver.Start`.

Risks: credentials are not automatically generated into usable values, so this may require manual web UI interaction before tests can pass. External image availability matters.

Test signals: connect probe to API port and valid S3 authentication/config.
