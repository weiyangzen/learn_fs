# sources/distributed-fs/xrootd/src/XrdSciTokens/test/create-pubkey.py

## Purpose

`create-pubkey.py` is a Python 2 integration-test helper that creates a SciToken signed by `private.pem`, optionally adds an audience claim, sends it to the local xrootd HTTP endpoint, and prints the fetched file contents.

## Important APIs, Types, And Functions

- Uses `argparse` for optional `--aud` and required JWKS public-key path.
- Loads `private.pem` with `cryptography` serialization.
- Reads the JWKS file to extract the first key's `kid`.
- Creates `scitokens.SciToken(key=private_key, key_id=key_id)`, sets `scope = "read:/"`, optionally sets `aud`, serializes with issuer `https://localhost`, and sends `Authorization: Bearer <token>` to `http://localhost:8080/tmp/random.txt` via `urllib2`.

## Control Flow

The script is invoked by `test_inside_docker.sh` after Apache serves JWKS and xrootd serves `/tmp`. Its stdout is compared with a generated random file value. A nonzero exception path is used by shell `if python ...; then exit 1` checks to assert expected failures.

## State And Persistence

It reads `private.pem` and the JWKS file, makes a network request, and writes only stdout/stderr.

## Dependencies And Integration Points

It depends on Python 2 modules `urllib2`, `scitokens`, `cryptography`, and `json`. It integrates with generated test keys, the local issuer metadata served by Apache, and xrootd HTTP authorization.

## Risks And Edge Cases

- Python 2 dependency is obsolete and environment-sensitive.
- It assumes `private.pem` is in the current working directory.
- It always requests `read:/` and one fixed URL, so it does not exercise write or path-restricted scopes.
- It extracts only the first JWKS key ID.

## Test Signals

Successful execution prints the contents of `/tmp/random.txt`. Expected failure cases include wrong/missing audience under audience-requiring configs and audience-present tokens under no-audience config.
