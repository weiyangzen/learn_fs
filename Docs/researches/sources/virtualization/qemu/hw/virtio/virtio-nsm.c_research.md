# File Research: sources/virtualization/qemu/hw/virtio/virtio-nsm.c

Implements a virtio AWS Nitro Secure Module (NSM) device with CBOR request parsing, CBOR responses, PCR state, random data, attestation document construction, virtqueue handling, migration of PCRs, and the `module-id` property.

Key entry points:
- `virtio_nsm_device_realize()` initializes default NSM identity/version/digest callbacks, creates the virtio device with `VIRTIO_ID_NITRO_SEC_MOD`, and adds a two-entry virtqueue.
- `handle_input()` consumes one request buffer and one response buffer from the virtqueue, validates buffer structure, builds the response, pushes both elements, and notifies the guest.
- `get_nsm_request_response()` enforces maximum request size, identifies the CBOR command, and calls the command handler.
- Command handlers implement `GetRandom`, `DescribeNSM`, `DescribePCR`, `ExtendPCR`, `LockPCR`, `LockPCRs`, and `Attestation`.
- `extend_pcr()` updates a PCR using SHA-384 over old PCR data concatenated with caller data.

Protocol dispatch:
- `get_nsm_request_cmd()` accepts two request forms: a root CBOR string for simple commands and a one-entry root map whose key is the command string for parameterized commands.
- The static `nsm_cmds[]` table maps command name, root type, and response function.
- Requests larger than `NSM_REQUEST_MAX_SIZE` return `InputTooLarge`.
- Unknown or malformed commands return `InvalidOperation`.

Virtqueue behavior:
- The device expects the first popped element to contain a nonempty outgoing request.
- It expects a second popped element containing an input response buffer exactly `NSM_RESPONSE_BUF_SIZE` bytes long.
- Request data is copied into a temporary contiguous buffer, and the serialized response is copied back to the input buffer.
- On success, the request element is pushed with used length 0 and the response element with the serialized response length.
- Structural virtqueue violations call `virtio_error()` and detach any popped elements.

Command behavior:
- `GetRandom` returns 256 bytes from `qemu_guest_getrandom_nofail()`.
- `DescribeNSM` returns digest string, max PCR count, module id, locked PCR indices, and version 1.0.0.
- `DescribePCR` parses an 8-bit `index`, validates it against `max_pcrs`, and returns PCR data and lock state.
- `ExtendPCR` parses 8-bit `index` and string/bytes `data`, rejects invalid or locked PCRs, extends the PCR, and returns the new digest.
- `LockPCR` parses an 8-bit `index`, rejects invalid or already locked PCRs, marks it locked, and returns a success string.
- `LockPCRs` parses an 8-bit `range`, validates it does not exceed `max_pcrs`, locks PCR indices below that range, and returns a success string.
- `Attestation` parses optional `public_key`, `user_data`, and `nonce` as byte/string/null properties and returns an attestation document.

Attestation document:
- The response wraps a serialized COSE Sign1-like array in a CBOR `Attestation.document` byte string.
- Protected header encodes algorithm `-1`; comments note the document is not actually signed.
- Unprotected header is an empty map.
- Payload includes module id, digest, millisecond timestamp, locked PCR map, placeholder certificate, placeholder CA bundle, public key, user data, and nonce.
- Signature is a 64-byte zero byte string.

CBOR and error handling:
- `error_response()` serializes a one-entry CBOR map containing an error string.
- Parsers use libcbor type checks and exact-width checks for integer fields expected as `CBOR_INT_8`.
- String and byte-string inputs are both accepted for PCR extend data and attestation properties.
- Serialization failure due to response size returns `InputTooLarge` or `BufferTooSmall` depending on command context.

State and migration:
- `VirtIONSM` stores `NSM_MAX_PCRS` PCR entries with lock flag and SHA-384-sized data.
- VMState migrates the PCR array via `vmstate_pcr_info_entry`.
- The top-level virtio device state is migrated through `VMSTATE_VIRTIO_DEVICE`.
- `module-id` is a QOM string property; if unset, realize uses a default module id string.

Important invariants:
- PCR indices must be below `vnsm->max_pcrs`.
- Locked PCRs cannot be extended or locked again through `LockPCR`.
- Request size is capped before parsers copy string/bytes payloads into fixed-size request structs.
- Response buffer size is fixed and enforced by virtqueue handling.
- The implementation models attestation structure but uses placeholder certificate/CA/signature data.

Filesystem/block relevance:
- No filesystem or block behavior. It is a virtio security device that may be present in virtual machines running filesystems or storage workloads.

Notable risks:
- Attestation is structurally generated but not cryptographically signed; the code explicitly uses zero placeholder signature and certificate data.
- Some parser paths ignore unknown map keys, so malformed requests with extra keys can still be accepted if required keys are valid.
- `handle_input()` requires request and response as separate virtqueue elements in sequence, which is stricter than many virtio device request layouts.
