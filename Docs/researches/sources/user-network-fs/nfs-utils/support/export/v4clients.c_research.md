# sources/user-network-fs/nfs-utils/support/export/v4clients.c

## Purpose
Monitors `/proc/fs/nfsd/clients` with inotify and logs NFSv4 client attach/detach events, including transitions from unconfirmed to confirmed client state.

## Important APIs, Types, and Functions
Public functions are `v4clients_init()`, `v4clients_set_fds()`, and `v4clients_process()`. Internal state uses `struct ent`, `tsearch()` tree management, `read_info()`, `add_id()`, `del_id()`, and `check_id()`.

## Control Flow
Initialization verifies the procfs clients directory, opens a nonblocking inotify fd, and watches for create/delete events. Processing reads inotify events, parses numeric client ids from names, adds/removes tree entries, and watches each client `info` file for modifications while unconfirmed. `read_info()` extracts clientid, address, minor version, and status lines.

## State and Persistence Behavior
Process-global state includes `clients_fd`, a search tree of `struct ent` records, per-client info-file watch ids, and `have_unconfirmed`. State is not persisted beyond log messages and kernel procfs watches.

## Dependencies and Integration Points
Depends on Linux inotify, `/proc/fs/nfsd/clients`, `search.h`, and `export.h` logging. It integrates with mountd/exportd select loops through fd-set helpers.

## Risks and Edge Cases
Only numeric event names are accepted. Lost inotify events, disappearing info files, and unexpected procfs formats can drop logs. Tree entries are keyed by client directory number, not clientid content.

## Test Signals
Test no-procfs behavior, inotify setup failure, create/delete/modify events, unconfirmed-to-confirmed attach logging, confirmed detach logging, malformed info files, and nonnumeric event names.
