# File Research: sources/virtualization/nvme-cli/libnvme/test/config/data/tls_key-2.json

## Purpose
TLS key JSON fixture with explicit TLS PSK identity.

## Contents
Same basic host/subsystem/port structure as `tls_key-1.json`, but includes `tls_psk_identity` alongside the encoded `tls_key`.

## Relevance
Covers preservation/serialization of both PSK identity and key material in JSON config tests.
