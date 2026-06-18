# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/ptp/ptp.c

This file implements a USB PTP/MTP-like camera storage 9P server. It opens bulk IN/OUT endpoints, starts a PTP session, discovers storage ids and object handles, lazily maps them into a 9P tree, supports reading objects and thumbnails, supports deleting objects, and closes the session when the service exits.

The PTP transport uses `Ptprpc`, a fixed buffer for PTP command/data/response containers. `vptprpc()` builds operation requests, writes optional data phases, reads optional data phases, validates response type/transaction/code through `ptpcheckerr()`, decodes PTP response errors to strings, and extracts output parameters. Transfers are serialized through a single `Ioproc` sent over `iochan`; `ptprpc()` integrates that serialization with 9P request flush handling by racing I/O ownership against per-request interrupt channels.

Tree state is cached in `Node` objects indexed by qid path. `getnode()` lazily constructs root, storage, object, and thumbnail nodes by issuing `GetStorageInfo` or `GetObjectInfo`, decoding PTP UTF-16 strings, assigning directory/file modes, sizes, image-thumbnail names, object formats, parent/store/handle metadata, and timestamps from PTP date strings. `readchilds()` fills child lists by calling `GetStorageIds` or `GetObjectHandles`; image objects also get synthetic thumbnail nodes.

`fsread()` serves directories, attempts efficient partial file reads with `GetPartialObject`, and falls back to full `GetObject`/`GetThumb` caching. `fsremove()` maps object deletion to `DeleteObject` and frees cached object or thumbnail nodes. `fsdestroyfid()` releases cached object data when fids go away. `fsflush()` interrupts blocked PTP requests.

`threadmain()` opens/configures the USB device, finds bulk endpoints plus optional interrupt endpoint, opens endpoint data fds, creates the I/O process, opens a PTP session using the process id as session id, and posts the service as an `sdU...` tree with a `.ptp` service name.
