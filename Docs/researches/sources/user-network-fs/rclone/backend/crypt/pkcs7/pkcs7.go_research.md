# sources/user-network-fs/rclone/backend/crypt/pkcs7/pkcs7.go

Purpose: Implements PKCS#7 block padding and unpadding for cryptographic buffers whose lengths must be multiples of a block size.

Important APIs, types, and functions: Exported errors distinguish malformed padding cases. `Pad(n, buf)` appends padding bytes to the supplied slice. `Unpad(n, buf)` validates and strips padding, returning a subslice or a specific error.

Control flow: Both functions panic for invalid block sizes `n <= 1` or `n >= 256`. `Pad` computes `n - len(buf)%n`, appends that byte value repeatedly, and verifies the result is aligned. `Unpad` checks empty input, block alignment, padding length bounds, zero padding, and equality of all trailing padding bytes before slicing.

State and persistence behavior: There is no persistent state. `Pad` mutates/appends to the caller-provided slice, while `Unpad` returns a view into the original slice.

Dependencies and integration points: Depends only on `errors`. It is intended for use by crypt filename/data cipher code where exact padding validation matters for authentication and decode errors.

Risks: Callers must copy input before `Pad` if they need immutability. Panics on invalid block sizes are deliberate and should be kept away from user-controlled parameters. `Unpad` exposes detailed error reasons, which is useful internally but should not be converted into a padding oracle in network-facing contexts.

Test signals: `pkcs7_test.go` covers normal pad/unpad round trips, malformed padding variants, and invalid block-size panics.
