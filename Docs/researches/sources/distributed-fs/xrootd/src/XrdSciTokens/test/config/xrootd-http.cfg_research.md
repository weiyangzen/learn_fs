# sources/distributed-fs/xrootd/src/XrdSciTokens/test/config/xrootd-http.cfg

## Purpose

This test xrootd configuration starts a standalone data server exporting `/tmp`, enables HTTP on port 8080, and loads the SciTokens authorization plugin.

## Important APIs, Types, And Functions

- `all.export /tmp`, `all.adminpath /var/spool/xrootd`, and `all.pidpath /run/xrootd` configure the standalone server.
- `xrd.protocol XrdHttp:8080 /usr/lib64/libXrdHttp-4.so` loads HTTP.
- `http.header2cgi Authorization authz` maps the HTTP `Authorization` header into request CGI key `authz`.
- `ofs.authorize` enables authorization.
- `ofs.authlib libXrdAccSciTokens.so` loads the SciTokens plugin.
- `xrd.trace all` enables broad tracing for the test.

## Control Flow

`test_inside_docker.sh` installs this as `/etc/xrootd/xrootd-http.cfg`, starts `xrootd@http.service`, then HTTP requests with bearer tokens are checked by the SciTokens plugin before reading `/tmp/random.txt`.

## State And Persistence

The config produces runtime server state under admin/pid paths and serves files from `/tmp`.

## Dependencies And Integration Points

It depends on the HTTP plugin path used by the CentOS test packages, SciTokens authlib installation, systemd socket/service environment, and header-to-CGI integration expected by `XrdSciTokensAccess.cc`.

## Risks And Edge Cases

- Hard-coded `/usr/lib64/libXrdHttp-4.so` is distribution/version-specific.
- `xrd.trace all` is noisy and test-oriented.
- Exporting `/tmp` is appropriate for tests but not a production policy.

## Test Signals

Passing signal is an HTTP GET to `/tmp/random.txt` with a valid token returning the generated file contents while invalid audience cases fail.
