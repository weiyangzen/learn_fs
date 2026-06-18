# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/util.c

## Purpose
Core libnvme utility implementation: status/error conversion, string tables, hostname/address helpers, key-value parsing, UUID utilities, interface address matching, basename, and fabrics config copying.

## Main Logic
- Maps NVMe generic, command-specific, and fabrics status codes to errno-like values.
- Converts NVMe status codes and kernel errors to readable strings, including generic, command-specific, NVM, fabrics, media, path, and vendor-specific classes.
- Maps libnvme connect errors such as resolve failure, invalid transport, already connected, unsupported, ignored, or missing TLS key.
- Resolves hostnames to transport addresses when `NVME_HAVE_NETDB` is available.
- Provides `startswith()`, `kv_strip()`, and `kv_keymatch()` for simple config-style text parsing.
- Provides project/git version getters.
- Converts UUIDs to/from string form, generates RFC 4122-style random UUIDs, and searches identify UUID lists.
- Compares numeric IPv4/IPv6 addresses, including IPv4-mapped IPv6 cases, and locates matching network interfaces.
- Implements a stable `libnvme_basename()` independent of libc variant behavior.
- Provides `libnvme_fabrics_config_copy()` as the single copy point for fabrics config structs.

## Portability
Uses Windows BCrypt for random bytes when available, otherwise `/dev/urandom`. Network helpers degrade to logging and unsupported/false results when libnss/netdb support is absent.

## Relevance
This file supplies common support for command-result interpretation, NVMe-oF address handling, identity generation, and configuration parsing used throughout libnvme.
