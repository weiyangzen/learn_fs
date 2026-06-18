# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/nbft.c

## Role

Implements parsing for ACPI NBFT (NVMe Boot Firmware Table) files into libnvme's public `struct libnbft_info` model. It reads a raw NBFT binary file, validates global table structure, parses supported descriptors, links descriptors by NBFT index fields, and provides cleanup.

## Main Entry Points

- `libnvmf_read_nbft(ctx, nbft, filename)`: opens a raw NBFT file, reads it into memory, allocates `struct libnbft_info`, stores filename/raw table metadata, and calls `parse_raw_nbft()`.
- `libnvmf_free_nbft(ctx, nbft)`: frees descriptor lists, raw NBFT bytes, filename, and top-level object.
- `parse_raw_nbft(ctx, nbft)`: validates table header/control/host, then walks HFI, security, discovery, and SSNS descriptor arrays.

## Parsing Flow

- `csum()` computes the byte checksum required for ACPI-style table validation.
- `format_ip_addr()` converts 16-byte NBFT IPv6-style addresses to printable IPv4 if IPv4-mapped, otherwise IPv6.
- `in_heap()` validates `struct nbft_heap_obj` offset/length pairs against the NBFT heap range.
- `__get_heap_obj()` resolves a heap object pointer, optionally checks string NUL termination, and reports debug errors for invalid offsets or unterminated strings.
- `discovery_from_index()`, `hfi_from_index()`, and `security_from_index()` resolve previously parsed descriptors by NBFT index.

## Descriptor Support

- Host descriptor:
  - Requires `NBFT_HOST_VALID`.
  - Exposes raw host UUID pointer and heap-backed host NQN.
  - Sets `host_id_configured` and `host_nqn_configured`.
- HFI descriptors:
  - Supports TCP transport (`NBFT_TRTYPE_TCP`) only.
  - Parses TCP transport info descriptor, including PCI SBDF, MAC, VLAN, IP origin, IP/gateway/DNS/DHCP addresses, route metric, DHCP override, host name, and default-route flag.
- Discovery descriptors:
  - Parses discovery URI and discovery controller NQN.
  - Links optional HFI and security descriptors by index.
- SSNS descriptors:
  - Supports TCP only.
  - Parses transport address/service, NSID, NIDT/NID, subsystem NQN, digest flags, unavailable/discovered flags, primary discovery controller, primary/secondary HFI list, security descriptor, and optional extended info.
  - Deduplicates secondary HFI indexes and skips duplicate primary references.
- SSNS extended info:
  - Validates descriptor ID/version/index.
  - Applies ASQSZ if present, controller ID, and optional DHCP root path string.
- Security descriptors:
  - `read_security()` is currently a stub returning `-EINVAL`, so security descriptors are allocated as a list but none are populated.

## Validation and Error Behavior

- Uses a local `verify()` macro that logs `LIBNVME_LOG_DEBUG` with filename and returns `-EINVAL`.
- Header validation covers:
  - Minimum size.
  - Checksum equals zero.
  - Signature equals `NBFT`.
  - Header length does not exceed file size.
  - Major/minor revision exactly `1.0`.
  - Heap offset/length stays inside table length.
- Descriptor list bounds are checked against table length before walking arrays.
- Invalid optional descriptor references are often logged but not fatal, while missing required heap objects and invalid primary HFI are fatal for that descriptor.
- The `hfi_len`, `sec_len`, `disc_len`, and `ssns_len` parameters are accepted by descriptor-list readers but not used; the parser assumes fixed struct sizes for several descriptor arrays.

## Memory/Lifetime Model

Parsed string pointers and host ID point into `raw_nbft`; they are not separately allocated. `raw_nbft` must remain alive until `libnvmf_free_nbft()`. Parsed descriptor objects are separately allocated, but many fields are borrowed pointers into the raw table.

## Notable Implementation Details

- Descriptor pointer-array allocations use `sizeof(struct libnbft_*)` rather than pointer element size in multiple readers. This overallocates on typical platforms rather than underallocating, but the type intent is pointer-array storage.
- `read_security()` being unimplemented means linked security pointers are normally unresolved.
- `read_ssns_exended_info` is misspelled in the function name.
