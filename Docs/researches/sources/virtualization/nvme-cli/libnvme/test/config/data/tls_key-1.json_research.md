# File Research: sources/virtualization/nvme-cli/libnvme/test/config/data/tls_key-1.json

## Purpose
TLS key JSON fixture without explicit PSK identity.

## Contents
Defines one host and one TCP subsystem port with `tls:true`, `dhchap_key:"none"`, and an encoded `tls_key`.

## Relevance
Used to verify libnvme imports/exports encoded TLS keys and can dump normalized config.
