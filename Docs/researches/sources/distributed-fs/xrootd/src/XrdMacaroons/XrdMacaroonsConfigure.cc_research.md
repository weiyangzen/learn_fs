# sources/distributed-fs/xrootd/src/XrdMacaroons/XrdMacaroonsConfigure.cc

Purpose: Parses Macaroons plugin configuration and loads the shared secret key.

Important APIs/types/functions: `Handler::Config` reads `all.sitename` and `macaroons.*` directives. Helpers include `xonmissing`, `xtrace`, `xmaxduration`, `xsitename`, and `xsecretkey`.

Control flow: The config stream captures macaroons directives, initializes default trace mask and max duration, recognizes `macaroons.secretkey`, `all.sitename`/`macaroons.sitename`, `macaroons.trace`, `macaroons.maxduration`, and `macaroons.onmissing`, and ignores unknown directives with a warning. Secret-key loading opens a base64 file, decodes through OpenSSL BIO filters into memory, enforces at least 32 decoded bytes, and stores the raw secret string.

State and persistence: Outputs location, secret, max duration, and on-missing behavior by reference. The secret is held in memory by the caller. No files are written.

Dependencies and integration points: Uses `XrdOucStream`, `XrdSysError`, OpenSSL BIO/EVP, errno, and `Macaroons::Handler` enum/types from the handler header.

Risks: `errno` is not reset before `strtoll`, so stale errno could theoretically influence diagnostics after successful parse. Secret-key read loop has an unreachable inner `inlen < 0` branch inside `while ((inlen = BIO_read(...)) > 0)`, but the post-loop error path handles negative results. Missing `all.sitename` is fatal.

Test signals: Valid config, missing sitename, missing/short/unreadable secret file, trace option combinations including `none/off`, invalid onmissing, invalid maxduration, and unknown directive warnings.
