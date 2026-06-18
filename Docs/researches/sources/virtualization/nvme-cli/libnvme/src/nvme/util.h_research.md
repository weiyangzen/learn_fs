# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/util.h

## Purpose
Public/internal utility declarations for libnvme.

## Main Interfaces
- `enum libnvme_connect_err` defines libnvme-specific connection error codes starting at 1000.
- Status conversion APIs: `libnvme_status_to_errno()`, `libnvme_status_to_string()`, opcode-specific status helper, connect error string helper, and `libnvme_strerror()`.
- Inline opcode-specific status strings for sanitize namespace and set-features command-specific statuses.
- Fabrics extended-attribute iterator: `libnvmf_exat_ptr_next()`.
- Version selectors and `libnvme_get_version()`.
- UUID conversion/generation/search helpers.
- `libnvme_basename()`.

## Relevance
This header is the shared utility contract for libnvme callers and internal modules, especially around error presentation and portable identifiers.
