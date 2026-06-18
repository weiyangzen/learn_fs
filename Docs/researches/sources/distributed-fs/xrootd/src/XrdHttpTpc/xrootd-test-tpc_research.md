# sources/distributed-fs/xrootd/src/XrdHttpTpc/xrootd-test-tpc

Purpose: Python helper script to drive manual HTTP TPC COPY transfers using bearer tokens.

Important APIs/types/functions: `parse_args` handles token paths, push/pull/auto mode, overwrite, streams, source, and destination. `get_token` reads the first non-comment token line. `determine_mode` sends OPTIONS to the destination and chooses pull if COPY is advertised. `main` builds headers and sends the COPY request with `requests`.

Control flow: Token paths are resolved from explicit arguments, `SCITOKEN`, `~/.scitokens/token`, or `/tmp/scitoken_u<euid>`. In auto mode, OPTIONS decides whether destination can pull. Pull mode sends COPY to destination with `Source` and destination auth, plus `Copy-Header` for source auth. Push mode sends COPY to source with `Destination` and source auth, plus destination auth as `Copy-Header`.

State and persistence: No persistence beyond reading token files. It prints response status, headers, and body.

Dependencies and integration points: Uses Python `requests`, CA verification at `/etc/grid-security/certificates`, and the HTTP TPC plugin's headers (`Authorization`, `Source`, `Destination`, `Copy-Header`, `Overwrite`, `X-Number-Of-Streams`).

Risks: The script uses Python 2 print syntax and may not run under Python 3 despite a generic `#!/usr/bin/python`. It sets a fixed CA verification path and does not retry despite a `try_again` variable. Token content is injected into headers, so output/log handling should avoid leaking tokens.

Test signals: Run under the supported Python interpreter, test auto/pull/push modes, missing token discovery, stream validation, and successful COPY against a test pair of HTTP TPC endpoints.
