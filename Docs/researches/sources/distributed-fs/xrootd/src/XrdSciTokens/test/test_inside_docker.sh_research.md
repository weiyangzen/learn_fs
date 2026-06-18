# sources/distributed-fs/xrootd/src/XrdSciTokens/test/test_inside_docker.sh

## Purpose

`test_inside_docker.sh` provisions a CentOS container, builds and installs the xrootd-scitokens RPM, configures a local HTTPS issuer and xrootd HTTP server, then validates SciTokens audience behavior with real HTTP reads.

## Important APIs, Types, And Functions

- Installs EPEL, build tools, OSG repositories, `xrootd-server-devel`, `scitokens-cpp-devel`, `httpd`, `mod_ssl`, `xrootd-server`, and `python2-scitokens`.
- Builds RPM from `rpm/xrootd-scitokens.spec` using `git archive` and `rpmbuild`.
- Generates SciTokens keys with `scitokens-admin-create-key`, serves JWKS and OIDC discovery from Apache, and creates a self-signed certificate with `openssl-selfsigned.conf`.
- Installs xrootd and SciTokens configs, restarts `xrootd@http.service`, writes random data to `/tmp/random.txt`, and invokes `create-pubkey.py`.
- Exercises no-audience, single-audience, multi-audience, missing-audience, and wrong-audience scenarios.

## Control Flow

The script first prepares package repositories and build dependencies, builds the source RPM/binary RPM, installs it, configures Apache TLS/JWKS discovery, configures xrootd HTTP authorization, starts services, and then runs a sequence of token request assertions. For success cases, Python output must exactly equal the generated random string. For failure cases, the Python command must fail or the script exits with failure.

## State And Persistence

It mutates the container extensively: yum cache/repos/packages, `/tmp/rpmbuild`, `/etc/httpd`, `/var/www/html`, `/etc/ssl`, `/etc/xrootd`, systemd drop-ins, services, generated keys/certs, and `/tmp/random.txt`.

## Dependencies And Integration Points

It depends on external RPM repositories, network access, systemd, Apache, OpenSSL, SciTokens admin tooling, Python 2 client libraries, xrootd packages, and the local repository layout. It integrates the SciTokens plugin through `ofs.authlib` and HTTP authorization header mapping.

## Risks And Edge Cases

- Network and repository availability dominate reliability.
- `cat /dev/urandom | ... | head` can trigger pipefail-style issues if shell options change, though current script uses `-xe` not `pipefail`.
- The script assumes x86_64 RPM output and CentOS/OSG package names.
- It modifies global CA bundle and service configs inside the container.
- Audience expectations depend on SciTokens library semantics and exact issuer URL handling.

## Test Signals

The key test signal is exact content match for valid token cases and command failure for invalid audience cases. Additional signals are successful RPM build/install, Apache restart, xrootd restart, JWKS discovery availability, and service logs.
