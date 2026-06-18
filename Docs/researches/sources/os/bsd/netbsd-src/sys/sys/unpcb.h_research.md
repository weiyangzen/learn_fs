# File Research: sources/os/bsd/netbsd-src/sys/sys/unpcb.h

Read completely: 109 lines.

Defines Unix-domain socket protocol control block.

Key elements:
- `struct unpcb` links a socket to optional filesystem vnode/address, fake inode, connected peer, referencing sockets, stream lock, copied receive-buffer accounting, creation time, flags, and peer credential identity.
- Comments document vnode association, connection/reference topology, stream back-pressure accounting, and pipe creation time behavior.
- Flags cover wanted credentials, connect-wait behavior, valid peer IDs, bind-supplied peer IDs, busy connect/bind state, and newer credential passing.
- `sotounpcb(so)` casts a socket PCB to `struct unpcb *`.

Risks and notes:
- Reference topology can include many-to-one datagram references and peer links; lifecycle bugs can leak or dangle sockets/vnodes.
- Credential flags govern what identity information may be exposed to userland.
