# sources/user-network-fs/nfs-ganesha/src/tools/multilock/multilock.h

Purpose: `multilock.h` is the public interface and protocol contract for the multilock console and clients. It centralizes buffer sizes, command/status enums, client/response structures, parser/serializer prototypes, utility macros, and textual command/response documentation.

Important APIs and types: `MAXSTR`, `MAXDATA`, `MAXXFER`, and `MAXFPOS` bound protocol fields. `enum commands` defines OPEN, CLOSE, LOCKW, LOCK, UNLOCK, TEST, LIST, HOP, UNHOP, SEEK, READ, WRITE, COMMENT, ALARM, HELLO, FORK, and QUIT. `enum status` defines OK, AVAILABLE, GRANTED, DENIED, DEADLOCK, CONFLICT, CANCELED, COMPLETED, ERRNO, PARSE_ERROR, and ERROR. `struct client` stores socket streams, name, list links, and refcount. `struct response` stores parsed protocol fields and original text. `enum lock_mode` chooses POSIX vs OFD locks.

Control flow and integration: the header exposes parser helpers (`parse_request()`, `parse_response()`), formatters (`sprintf_req()`, `sprintf_resp()`), response list helpers, and send/respond functions implemented in `ml_functions.c`. Console and client files include it as the single protocol schema.

State and persistence: state is declared as extern globals: parser error buffers, `client_list`, `input`, `output`, mode flags, `global_tag`, `syntax`, and line number. The header does not persist data; it defines in-memory layouts and conventions.

Dependencies: it includes standard C/POSIX headers for file, socket, signal, select, netdb, and path constants. It conditionally defines Linux OFD lock constants if the platform headers do not.

Risks: the utility macros use GNU variadic macro syntax (`args...`) and assume arrays, not pointers, for `array_strcpy`/`array_strncpy`. `array_sprintf` computes but does not use `left` after one call. Protocol buffers are fixed-size; callers must maintain max lengths. `struct sockaddr c_addr` may not hold all address families even though current code uses IPv4.

Test signals: compile coverage should include systems with and without `F_OFD_*` constants. Protocol tests should confirm the documented command/response forms match the parser and formatter behavior.
