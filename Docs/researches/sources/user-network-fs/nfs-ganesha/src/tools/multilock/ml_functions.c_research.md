# sources/user-network-fs/nfs-ganesha/src/tools/multilock/ml_functions.c

Purpose: `ml_functions.c` is the shared multilock protocol library. It defines command/status names, token parsers, request/response serializers, response comparison, expected-response list management, global tag handling, and memory cleanup shared by the console and clients.

Important APIs, types, and functions: `commands[]`, token tables for on/off, lock types, read/write flags, open flags, and lock modes encode the text protocol. `readln()`, `SkipWhite()`, `get_token()`, `get_token_value()`, `get_long()`, `get_unsignedlonglong()`, `get_fpos()`, `get_rdata()`, `get_client()`, `get_status()`, and `get_open_opts()` are the parser primitives. `parse_request()` dispatches to `parse_open()`, `parse_lock()`, `parse_unlock()`, `parse_list()`, and related functions; `parse_response()` parses status-specific response payloads. `sprintf_req()`, `sprintf_resp()`, `send_cmd()`, and `respond()` serialize protocol messages. `compare_responses()` implements wildcard-like comparison using `-1` for numeric fields and `"*"` for strings.

Control flow: callers parse input into `struct response`, execute or send commands, then serialize output. Request parsing first obtains an optional/generated tag, command name, and command-specific payload. Response parsing obtains tag, command, status, and status-specific fields. The comparison path checks client, command, tag, status, and command/status payload fields before declaring a match.

State and persistence: globals include `errdetail`, `badtoken`, `client_list`, `input`, `output`, `script`, `quiet`, `duperrors`, `strict`, `error_is_fatal`, `global_tag`, `saved_tags[26]`, `syntax`, and `lno`. There is no durable persistence. Client objects are reference-counted through responses, and `free_client()` unlinks clients from `client_list`.

Dependencies and integration points: this file depends on `multilock.h`, C/POSIX string and file APIs, and lock constants such as `F_RDLCK`, `F_WRLCK`, and `F_UNLCK`. It is the compatibility layer binding `ml_console.c`, `ml_posix_client.c`, and `ml_glusterfs_client.c` to a single textual test grammar.

Risks: several parsing helpers compare `strtol`/`strtoull` end pointers to the post-token cursor, so whitespace/comment edge cases matter. The tag helpers use `if (tolower(*c) >= 'a' || tolower(*c) <= 'z')`, which is logically broad because of `||`; this can index `saved_tags` for non-letter bytes. `sprintf_*` helpers track remaining space but do not explicitly reject truncation. READ data is string-oriented and stores a NUL terminator, so binary data is not represented safely.

Test signals: test coverage should include round-trip parsing/formatting for every command, status-specific parser failures, generated tags and `$a` saved tags, wildcard comparisons, quoted strings with spaces, READ length mismatch, optional open flags and lock modes, and error reporting through `errdetail`/`badtoken`.
