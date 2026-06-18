# sources/security-integrity/selinux/libsepol/src/policydb_convert.c

## Purpose
Provides memory-image conversion helpers for policydbs: read a binary image into an initialized `policydb_t`, and write a `policydb_t` into a newly allocated memory image with verification.

## Important APIs, Types, and Functions
`policydb_from_image(sepol_handle_t *handle, void *data, size_t len, policydb_t *policydb)` wraps a memory-backed `policy_file_t` and calls `policydb_read`. `policydb_to_image(sepol_handle_t *handle, policydb_t *policydb, void **newdata, size_t *newlen)` runs `policydb_write` once in length-counting mode, allocates a buffer, writes into it, then verifies by reading the buffer into a temporary policydb.

## Control Flow
From-image initializes a `policy_file_t` as `PF_USE_MEMORY`, points it at caller memory, attaches the handle, and destroys the policydb on read failure before returning `STATUS_ERR`. To-image initializes `PF_LEN` to compute required size, switches to `PF_USE_MEMORY` with allocated storage, preserves original pointer/length because writing advances fields, writes the policy, then reinitializes the file view over the produced buffer and validates it with `policydb_read` into `tmp_policydb`.

## State and Persistence Behavior
The file is a persistence boundary between in-memory policydb state and serialized memory buffers. To-image transfers ownership of the allocated buffer to the caller only on success; on failure it frees the temporary buffer. Verification creates and destroys a temporary policydb. Error paths set `errno` to `EINVAL` for invalid policy/write/read failures and `ENOMEM` for temporary policydb initialization failure.

## Dependencies and Integration Points
Depends on `policy_file_init`, `policydb_read`, `policydb_write`, `policydb_init`, and `policydb_destroy`. Public wrappers in `policydb_public.c` expose these helpers as `sepol_policydb_from_image` and `sepol_policydb_to_image`.

## Risks and Edge Cases
If verification `policydb_read()` fails after `policydb_init(&tmp_policydb)` succeeds, the temporary policydb is not destroyed on that error path, creating a leak. From-image destroys the caller-supplied policydb on invalid image, which is important ownership behavior for callers. Zero-length images will fail in `policydb_read`; no precheck is done here. `policydb_to_image()` relies on writer length mode exactly matching writer memory mode.

## Test Signals
Tests should cover valid image read, invalid image cleanup and errno, write length computation, write/read verification, ownership of returned buffer, failure injection for allocation and write errors, and leak checks for verification failure paths.
