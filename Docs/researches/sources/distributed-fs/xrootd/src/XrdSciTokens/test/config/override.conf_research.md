# sources/distributed-fs/xrootd/src/XrdSciTokens/test/config/override.conf

## Purpose

This systemd drop-in injects an environment variable for the xrootd HTTP test service.

## Important APIs, Types, And Functions

- `[Service] Environment=REQUESTS_CA_BUNDLE=/localhost.crt` tells Python/request clients or related tooling to trust the self-signed localhost certificate during tests.

## Control Flow

`test_inside_docker.sh` copies this file into `/etc/systemd/system/xrootd@http.service.d/override.conf`, reloads systemd, and restarts the service.

## State And Persistence

The file persists as a systemd override inside the test container until removed.

## Dependencies And Integration Points

It integrates with the test-generated `localhost.crt`, systemd service environment, and SciTokens HTTPS/JWKS discovery.

## Risks And Edge Cases

- It assumes the certificate exists at `/localhost.crt`; the setup script copies certs under `/etc/ssl` but also generates in the working directory, so path assumptions matter.
- This is test-only and should not be installed in production.

## Test Signals

Test signal is successful HTTPS access to localhost issuer metadata without CA verification failures.
