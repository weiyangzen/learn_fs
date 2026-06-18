# File Research: sources/os/plan9/plan9/sys/src/cmd/webfs/dat.h

This header defines the core `webfs` data model.

Structures:
- `Ibuf`: buffered fd reader paired with an `Ioproc`.
- `Ctl`: per-client/global controls for accepting cookies, sending cookies, redirect limit, and user-agent.
- `Client`: active web request/session state, including URL/base URL, controls, request channel, content type, post body, redirect/auth state, extension for plumbed body path, I/O busy flag, body-open flag, I/O proc, refcount, and scheme auxiliary state.
- `Url`: parsed URL with scheme type, original URL, scheme/open/read/close callbacks, authority/user/pass/host/port/path/query/fragment, and scheme-specific HTTP/FTP fields.

URL scheme enum:
- `USunknown`, `UShttp`, `UShttps`, `USftp`, `USfile`, `UScurrent`.

Global declarations:
- Client table and counts.
- Debug flags.
- Global controls.
- 9P server `fs`.
- `status[]`.

Role:
- Shared internal ABI for all `webfs` implementation files.
