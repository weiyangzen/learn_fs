<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/client/client_proto.h -->
# sources/user-network-fs/samba/source3/client/client_proto.h

## Purpose
Frozen collected-prototypes header for source3 client code. It publishes the small subset of `client.c` and DNS browsing symbols needed by other client compilation units.

## APIs, Types, and Functions
The header forward-declares `struct cli_state` and `struct file_info`, defines the `ATTR_UNSET` and `ATTR_SET` enum used by DOS attribute mutation, and declares `client_get_cur_dir()`, `client_set_cur_dir()`, `client_clean_name()`, `do_list()`, `set_remote_attr()`, and `do_smb_browse()`. `do_smb_browse()` is declared twice in this snapshot.

## Control Flow, State, and Persistence
There is no runtime logic or persistence. The header fixes compile-time contracts for command helpers, list callbacks, path cleanup, current-directory access, and remote attribute updates. The attribute enum values must match `client.c`'s expectations for `set_remote_attr()` and `cmd_setmode()`.

## Dependencies and Integration
Includes depend indirectly on Samba core types such as `TALLOC_CTX`, `NTSTATUS`, and `uint32_t` from surrounding include order. `client.c` includes it, and other source3 client files such as tar or browse-related code can call the listed helpers without including the full client implementation.

## Risks and Test Signals
Risks include stale frozen prototypes when `client.c` signatures change, the duplicate `do_smb_browse()` declaration hiding accidental edits, and reliance on external include order for base Samba types. Build coverage of client tools is the key signal, plus compile failures when callback signatures or enum use drift.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/client/client_proto.h -->
