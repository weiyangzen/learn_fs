# sources/distributed-fs/xrootd/src/XrdSciTokens/test/openssl-selfsigned.conf

## Purpose

This OpenSSL config creates a self-signed localhost certificate for the SciTokens integration test HTTPS issuer.

## Important APIs, Types, And Functions

- `[req]` sets 2048-bit default key, `localhost.key`, distinguished-name section, request extensions, and x509 extensions.
- `[localhost]` supplies subject defaults for US/Nebraska/Lincoln/SciTokens/Development/commonName localhost.
- `[req_ext]` and `[v3_ca]` use `subjectAltName = @alt_names`.
- `[alt_names]` contains `DNS.1 = localhost` and `DNS.2 = 127.0.0.1`.

## Control Flow

`test_inside_docker.sh` passes this file to `openssl req -x509 -nodes -days 365 -newkey rsa:2048 ...` to generate `localhost.key` and `localhost.crt`.

## State And Persistence

The config itself is static. Generated key/cert files persist in the test container and are copied into `/etc/ssl`.

## Dependencies And Integration Points

It integrates with Apache TLS config, SciTokens issuer discovery over HTTPS, and the system trust bundle update in the test script.

## Risks And Edge Cases

- `DNS.2 = 127.0.0.1` uses a DNS SAN for an IP literal rather than an IP SAN, which some TLS stacks may reject.
- Certificate values are test-only and not suitable for production.

## Test Signals

OpenSSL generation should succeed, Apache should restart with the certificate, and SciTokens/JWKS discovery should validate against the updated trust bundle.
