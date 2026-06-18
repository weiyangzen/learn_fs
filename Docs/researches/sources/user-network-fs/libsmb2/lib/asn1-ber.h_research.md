# sources/user-network-fs/libsmb2/lib/asn1-ber.h

Purpose: Defines BER tag constants, context structures, OID storage, and function prototypes for ASN.1 BER encoding/decoding.

Important APIs/types/functions: `ber_type_t` enumerates universal and application-specific BER tags. `struct asn1ber_context` carries input/output buffers and cursor offsets. `struct asn1ber_oid_value` stores up to `BER_MAX_OID_ELEMENTS` 32-bit OID components. Macros `ASN1_SEQUENCE`, `ASN1_CONTEXT`, and `ASN1_CONTEXT_SIMPLE` construct tag bytes.

Control flow: Header-only declarations; callers allocate and initialize contexts, then call parse/encode functions in protocol order.

State/persistence: Exposes cursor state fields directly, making the API lightweight but requiring callers to preserve invariants (`src_tail <= src_count`, `dst_head <= dst_size`).

Dependencies/integration: C/C++ compatible via `extern "C"`. Uses `config.h` and `<stdint.h>` conditionally. Function names map one-to-one with `asn1-ber.c`.

Risks: Directly exposed context fields make misuse easy. `src_count`, `src_tail`, `dst_size`, and `dst_head` are `int`, while lengths passed to APIs are often `uint32_t`, so caller-side conversions matter for large buffers. The license URL typo in the comment is nonfunctional.

Test signals: Compile from C and C++; include header with minimal prerequisites; unit-test each prototype against `asn1-ber.c` and verify OID boundary behavior at `BER_MAX_OID_ELEMENTS`.
