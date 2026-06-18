# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/linux.h

Public Linux-specific libnvme utility declarations, mostly around authentication/key handling and host identity.

Key API areas:
- DH-HMAC-CHAP:
  - HMAC algorithm enum
  - DHCHAP key generation
  - raw secret creation
- Linux keyring operations:
  - lookup keyring
  - describe key serial
  - lookup key
  - link keyring into session keyring
  - read/update key payload
- TLS PSK handling:
  - scan TLS keys
  - insert retained TLS keys
  - versioned/compat insertion
  - generate TLS key identity
  - revoke TLS keys
  - export/import PSK interchange format
- Host identity:
  - generate host NQN
  - generate host NQN from host ID
  - generate host ID
  - read host NQN/host ID from default config locations

Research notes:
- This header is declaration-only in the researched group; implementations are elsewhere in libnvme.
- The APIs bridge NVMe/TCP security material with Linux kernel keyrings and libnvme configuration flows.
