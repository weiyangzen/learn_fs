# sources/user-network-fs/samba/source4/torture/libnetapi/libnetapi_server.c

## Purpose
This file provides a small NetAPI server test focused on `NetRemoteTOD`.

## Important APIs, types, and functions
`torture_libnetapi_server()` initializes a libnetapi context, fetches the target host from torture settings, calls `NetRemoteTOD` once, then calls it ten more times while freeing each returned buffer with `NetApiBufferFree`.

## Control flow
After context initialization, the test performs the time-of-day call, validates status, frees the buffer, loops ten times to catch repeated allocation/free or connection reuse issues, and reports a formatted libnetapi error on failure.

## State and persistence behavior
The test is read-only on the remote server. It allocates and frees NetAPI buffers and a libnetapi context.

## Dependencies and integration points
It depends on `<netapi.h>`, `torture_libnetapi_init_context()`, and `libnetapi_get_error_string()`. It is registered by `libnetapi.c` as the `server` subtest.

## Risks and edge cases
The test requires the target host setting and server support for remote time-of-day queries. Repeated calls mainly catch memory-management or context reuse regressions.

## Test signals
Success means `NetRemoteTOD` works reliably through libnetapi and returned buffers can be freed repeatedly without API errors.
