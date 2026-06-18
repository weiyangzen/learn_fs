# sources/user-network-fs/samba/source4/lib/tls/tlscert.c

## Purpose

`tlscert.c` autogenerates a temporary self-signed CA certificate, host certificate, and private key for Samba TLS use when configured TLS files do not already exist.

## Important APIs, Types, and Functions

The public function is `tls_cert_generate()`. It uses GnuTLS X.509 certificate/private-key objects, constants for organization/unit/common names, a 700-day lifetime, and `RSA_BITS`, which selects 3072 bits in FIPS mode and 4096 bits otherwise.

## Control Flow

The function first refuses to run if any of key, cert, or CA files already exists. It generates host and CA private keys, creates a CA certificate with CA/key-cert-sign usage, creates a host certificate with DNS subject alt names for the primary and additional hostnames, signs the host certificate with the CA key path, exports host cert, CA cert, and private key as PEM, and saves the private key with mode `0600`. A macro funnels GnuTLS failures to a common failure label.

## State and Persistence Behavior

This file persists new PEM files to the configured paths. It does not overwrite partial existing TLS material. Generated certificates use current time for activation/serial and expire after the fixed lifetime.

## Dependencies and Integration Points

It depends on GnuTLS X.509 APIs and Samba file helpers `file_exist()`, `file_save()`, and `file_save_mode()`. Server TLS parameter setup in `tls_tstream.c` calls this when the CA file is absent.

## Risks and Edge Cases

The all-or-nothing guard skips generation if only one of the three files exists, which can leave incomplete TLS configuration for callers to diagnose later. The failure path logs but does not clean up files already written before a later failure. The generated CA and host certificate are temporary self-signed material, so strict external trust still requires proper CA deployment.

## Test Signals

Tests should cover clean autogeneration, existing-file skip behavior, additional SANs, FIPS/non-FIPS key sizes, private-key file mode, unwritable parent directories, and server parameter setup consuming the generated files.
