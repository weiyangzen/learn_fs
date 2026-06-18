<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/request-key.conf -->
# sources/security-integrity/keyutils/request-key.conf

## Purpose

`request-key.conf` is the default request-key policy file. It maps key request operations, key types, descriptions, and callout-info patterns to resolver programs.

## Important APIs, Types, and Functions

The file documents supported macros: `%%`, `%o`, `%k`, `%t`, `%d`, `%c`, `%u`, `%g`, `%T`, `%P`, and `%S`. Active rules resolve `dns_resolver` through `/sbin/key.dns_resolver`, debug user keys through `keyctl negate`, `keyctl reject`, a piped `/bin/cat`, or `request-key-debug.sh`, and generic negate through `/bin/keyctl negate`.

## Control Flow

At runtime `request-key.c` scans these rules, matches fields with wildcard support, chooses the least-wild matching line, expands macros, and executes the command. Lines beginning with `|` run in pipe mode where callout info is stdin and stdout becomes key payload.

## State and Persistence Behavior

The file itself is static configuration. Its actions can instantiate, reject, revoke, expire, or negate kernel keys depending on matched requests.

## Dependencies and Integration Points

It integrates with `/sbin/request-key`, `/sbin/key.dns_resolver`, `/bin/keyctl`, `/bin/cat`, and `/usr/share/keyutils/request-key-debug.sh`. It is part of system key resolver policy and test setup.

## Risks and Edge Cases

Rule order and wildcard specificity affect resolver selection. Hard-coded binary paths must match installation layout. Piped debug rules can echo arbitrary callout data into key payloads and are suitable for tests/debugging, not broad trust decisions.

## Test Signals

Request-key valid and piped tests should resolve `user debug:*` requests, attach results to expected keyrings, and exercise negate/reject/expired/revoked callout forms.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/request-key.conf -->
