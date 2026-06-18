# File Research: sources/os/bsd/netbsd-src/lib/libwrap/update.c

## Summary
Implements controlled initialization and variadic updates for TCP wrappers `request_info` structures.

## Main Responsibilities
- Zero-initialize `request_info` from a static default instance.
- Set default fd to `-1`, daemon to `unknown`, pid to `getpid()`, and back-pointers from host records to the request.
- Apply variadic key/value updates for file descriptor, daemon, user, client/server names, client/server addresses, and client/server sockaddr pointers.
- Warn and stop processing on invalid update keys.

## Key Interfaces
- `request_init(struct request_info *request, ...)`.
- `request_set(struct request_info *request, ...)`.
- Static `request_fill()` update engine.

## Risks
The variadic API is type-sensitive and lacks compile-time checking. String fields are truncated to `STRING_LENGTH`; sockaddr pointers are stored directly and must remain valid.
