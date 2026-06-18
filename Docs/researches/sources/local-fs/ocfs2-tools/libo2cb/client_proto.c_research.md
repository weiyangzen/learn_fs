# File Research: sources/local-fs/ocfs2-tools/libo2cb/client_proto.c

## Purpose

Implements the fixed-size local socket protocol used by ocfs2-tools/libo2cb to communicate with `ocfs2_controld`.

## Main Contents

- Defines a `client_message` table mapping message enum values to command strings, argument counts, and `printf` formats.
- `message_to_string()` returns command text for a message enum.
- `full_read()` and `full_write()` enforce complete fixed-size reads/writes, retrying `EINTR` and treating EOF/zero write as `EPIPE`.
- `send_message()` formats a message into an `OCFS2_CONTROLD_MAXLINE` buffer and writes the full fixed-size frame.
- `get_args()`, `receive_message_full()`, and `receive_message()` parse incoming fixed-size frames, validate command and argument count, and optionally return unparsed rest data.
- `parse_status()` and internal `parse_itemcount()` validate numeric fields.
- `receive_list()` consumes the protocol pattern `ITEMCOUNT`, repeated `ITEM`, then `STATUS 0 OK`, with error cleanup.
- `free_received_list()` frees list responses.
- `client_listen()` and `client_connect()` create abstract UNIX-domain sockets using `sun_path[1]`.

## Dependencies and Integration

- Depends on `o2cb/o2cb_client_proto.h` for message enum and line/argument limits.
- Used by `o2cb_abi.c` userspace-stack operations for mount, unmount, list clusters, and debug dump requests.

## Research Notes

- Protocol frames are always `OCFS2_CONTROLD_MAXLINE` bytes, simplifying daemon parsing at the cost of fixed buffer size.
- Abstract socket paths are copied with `strcpy` into `sun_path[1]`; callers must provide valid bounded paths.
