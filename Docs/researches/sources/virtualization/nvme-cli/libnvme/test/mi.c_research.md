# File Research: sources/virtualization/nvme-cli/libnvme/test/mi.c

## Role

`mi.c` tests libnvme’s Management Interface command and Admin-over-MI implementation using an in-memory custom MI transport. It avoids real MCTP sockets and instead directly inspects MI request/response headers and payloads.

## Test Harness

The file defines `test_transport`, whose submit callback initializes a default response, mirrors the request’s NMP response bit, and optionally invokes a per-test callback. `libnvme_mi_open_test()` creates an endpoint with this transport and marks quirks as already probed unless a test resets that state.

`test_transport_resp_calc_mic()` computes the response MIC using libnvme’s internal CRC helper. Tests use this to distinguish valid protocol failures from MIC failures.

## Coverage

Endpoint and controller lifecycle tests verify global endpoint lists and per-endpoint controller lists. Transport description tests verify fallback and custom endpoint descriptions.

Protocol validation covers successful MI data reads, transport failure, invalid MIC, too-small response headers, response-as-request errors, invalid message type, command slot indicator request setting, and CSI mismatch handling.

Admin-over-MI tests inspect raw request bytes for identify controller, identify namespace/list variants, namespace management create/delete, namespace attach/detach, firmware download and commit, format NVM, sanitize NVM, get/set features, and split get-log behavior. They also validate error propagation from MI response status and NVMe completion status.

Format validation rejects unaligned request/response sizes, bad offsets, too-large responses, impossible payload combinations, and invalid MI transfer lengths before any transport submission happens.

Additional tests cover configuration get/set operations, MCTP MTU endianness, SMBus frequency acceptance/rejection, endpoint quirk probing, and Admin transfer DLEN/DOFF field behavior for request and response payloads.

## Dependencies

- Uses public `<libnvme.h>` and `<libnvme-mi.h>`.
- Includes private libnvme headers for endpoint and transport internals.
- Uses CCAN endian and array-size helpers.
- Uses `utils.h` log helpers.

## Filesystem/Storage Relevance

This file validates NVMe management command construction and response parsing, especially for admin commands tunneled through an out-of-band management path.
