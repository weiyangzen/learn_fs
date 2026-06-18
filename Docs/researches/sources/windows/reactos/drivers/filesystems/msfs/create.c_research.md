# File Research: sources/windows/reactos/drivers/filesystems/msfs/create.c

This file implements mailslot create/open and close paths.

`MsfsCreate` opens the client side of an existing mailslot. It allocates a CCB, searches the global FCB list by case-insensitive filename, inserts the CCB into the matching FCB’s CCB list, increments the FCB reference count, and attaches FCB/CCB to the file object. If no mailslot exists, it returns `STATUS_UNSUCCESSFUL`.

`MsfsCreateMailslot` creates the server side. It allocates an FCB, copies the mailslot name, allocates a server CCB, initializes CCB/message/pending-IRP lists and locks, initializes the cancel-safe queue, checks for duplicate names, inserts the FCB globally, and attaches the server CCB to the file object.

`MsfsClose` decrements the FCB reference count, removes and frees the CCB, and if the closing handle is the server CCB, it drains queued messages and clears `ServerCcb`. When the reference count reaches zero, it removes and frees the FCB and name buffer.

Research notes:
- Global FCB list access is serialized with a mutex.
- Per-FCB CCB and message lists use spin locks.
- Duplicate mailslot creation fails with `STATUS_UNSUCCESSFUL`, not a more specific collision status.
