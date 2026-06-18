# File Research: sources/os/plan9/plan9/sys/src/cmd/webfs/fns.h

This header declares `webfs` internal functions by implementation file.

Covered APIs:
- Buffered input: `initibuf`, `readibuf`, `unreadline`, `readline`.
- Client management and control: `newclient`, `closeclient`, `clonectl`, `ctlwrite`, client/global ctl helpers, `plumburl`.
- Cookie operations: read/write/open/clunk/init/close, HTTP set-cookie, outgoing cookie formatting.
- Filesystem init: `initfs`.
- HTTP scheme implementation: `httpopen`, `httpread`, `httpclose`.
- I/O helpers: `iotlsdial`, `ioprint`.
- Plumbing: `plumbinit`, `plumbstart`, `replumb`.
- URL operations: parse/free/rewrite/set query/copy/escape/unescape/init.
- Utility allocation/string helpers.

Role:
- Central prototype list for all `webfs` C files and sample clients.
