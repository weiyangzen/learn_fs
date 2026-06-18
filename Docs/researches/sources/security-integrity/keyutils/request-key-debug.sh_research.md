<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/request-key-debug.sh -->
# sources/security-integrity/keyutils/request-key-debug.sh

## Purpose

`request-key-debug.sh` is a simple debug helper invoked from `request-key.conf` for user keys with `debug:*` descriptions. It instantiates requested keys with a predictable payload or negates them when the callout info asks for `neg`.

## Important APIs, Types, and Functions

The script expects positional arguments `<keyid> <desc> <callout> <session-keyring>`. It uses the `keyctl instantiate` and `keyctl negate` CLI operations and prints diagnostic context.

## Control Flow

It echoes the request parameters. If the callout string is not `neg`, it instantiates the in-progress key with payload `Debug <callout>` into the supplied session keyring. If the callout is `neg`, it dumps `/proc/keys`, prints the negate command, and negates the key for 30 seconds.

## State and Persistence Behavior

The script mutates kernel key state by instantiating or negating the requested key. It reads `/proc/keys` only for debug output and writes diagnostics to stdout.

## Dependencies and Integration Points

It is referenced by `request-key.conf` and depends on `/bin/sh`, `keyctl`, and `/proc/keys`. It is part of request-key callout testing for debug user keys.

## Risks and Edge Cases

Arguments are unquoted in echo output and the script assumes `keyctl` is in PATH. It is intentionally diagnostic and should not be used as a privileged general-purpose production resolver.

## Test Signals

Requesting `user debug:<name>` with arbitrary callout should instantiate a key readable as `Debug <callout>`; callout `neg` should produce a negatively instantiated key.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/request-key-debug.sh -->
