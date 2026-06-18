
# sources/security-integrity/keyutils/key.dns_resolver.c

## Purpose
`key.dns_resolver.c` implements the `key.dns_resolver` userspace helper for Linux request-key DNS resolution. It reads a kernel key request or debug-mode description, resolves A/AAAA or AFSDB-style names, builds a comma-separated payload, sets key timeout, and instantiates or rejects the kernel key.

## Important APIs, Types, And Functions
Logging/error functions are `error()`, `_error()`, `warning()`, `info()`, `_nsError()`, `nsError()`, and `debug()`. Payload functions are `append_address_to_payload()` and `dump_payload()`. Resolver logic is in `dns_resolver()` and `dns_query_a_or_aaaa()`. Configuration is handled by `read_config()` and `config_dumper()`. `main()` parses options, reads key description/callout info, validates key type, dispatches query type, and exits via no-return query helpers.

## Control Flow
Startup parses `-c`, `-D`, `--dump-config`, `-v`, and `-V`, then reads configuration. In normal mode it expects a key serial, describes the key with `keyctl_describe_alloc()`, and reads callout info from `KEY_SPEC_REQKEY_AUTH_KEY`. In debug mode it accepts a description and callout info directly. Descriptions without `type:name` go through A/AAAA resolution; `a:` and `aaaa:` dispatch to the same A/AAAA resolver; `afsdb:` dispatches to `afs_look_up_VL_servers()`.

`dns_query_a_or_aaaa()` parses options such as `ipv4`, `ipv6`, and `list`, calls `dns_resolver()`, rejects empty/no-data results, appends a terminating NUL segment, and instantiates the key. `dns_resolver()` calls `getaddrinfo()`, filters by `mask`, converts addresses with `inet_ntop()`, optionally appends a port suffix, deduplicates through `append_address_to_payload()`, and honors `ONE_ADDR_ONLY`.

## State And Persistence
Global state includes `key`, `verbose`, `debug_mode`, `mask`, `key_expiry`, `payload`, and `payload_index`. Non-debug success calls `keyctl_set_timeout()` and `keyctl_instantiate_iov()`. DNS failures call `keyctl_reject()` with short timeout mapping; fatal helper errors call `keyctl_negate()`.

## Dependencies And Integration Points
The helper depends on keyutils APIs, libresolv/h_errno behavior, `getaddrinfo()`, syslog, `/etc/keyutils/key.dns_resolver.conf`, `/etc/request-key.conf` integration, and `dns.afsdb.c` for AFS lookups. It is installed by the Makefile as `/sbin/key.dns_resolver`.

## Risks
`append_address_to_payload()` silently stops when `N_PAYLOAD` is near exhaustion. Address string buffers leave room for IPv6 plus port suffix, but port formatting assumptions come from AFS SRV code. Config parsing is strict and exits on malformed explicit config. Debug and normal modes have different input trust boundaries. `--config` is declared with no argument in `long_options` despite `-c` requiring one, which is a CLI parsing risk for long-form config use.

## Test Signals
Useful tests cover debug-mode A/AAAA lookup, option parsing, list versus single-address payloads, IPv4/IPv6 filtering, config default TTL parsing and dump, unsupported query rejection, key description parsing, and AFSDB/SRV dispatch. Integration tests require request-key and kernel keyring behavior.
