# File Research: sources/os/bsd/netbsd-src/lib/libwrap/refuse.c

## Summary
Logs and terminates a refused TCP wrappers request.

## Main Responsibilities
- Emit a denial log message using `deny_severity`.
- Format the remote endpoint through `eval_client(request)`.
- Terminate through `clean_exit(request)` so datagram services drain pending input and avoid inetd loops.

## Key Interfaces
- `refuse(struct request_info *request)`.

## Risks
This function does not return. Correct behavior depends on `clean_exit()` handling protocol-specific cleanup, especially for datagram-oriented services.
