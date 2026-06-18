# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh2/netssh.h

This header defines the shared protocol constants, qid layout, state structures, and function interfaces for `netssh`.

Key contents:
- `MYID`, packet/message constants, SSH disconnect/open reason constants, channel extended-data constants, and connection/channel state names.
- Qid path encoding for top-level, connection-level, and subchannel-level files.
- Core structures: `Conn`, `SSHChan`, `Packet`, `Cipher`, `Kex`, `PKA`, `MBox`, and packet queue `Plist`.
- File pointers for each synthetic 9P node exposed by connections and channels.
- Transport, Diffie-Hellman, public-key, and keyring helper prototypes.

Important details:
- `Conn` stores both current and next cipher/MAC state and derived key material.
- `SSHChan` stores queues for data and request packets plus channel windows and synchronization primitives.
- `MAXCONN` is derived from qid bit allocation and doubles as max channel count.
- `Packet` embeds a fixed `Maxpktpay` payload buffer.

Filesystem relevance:
- Central: defines the data model and qid namespace for `/net/ssh`.
