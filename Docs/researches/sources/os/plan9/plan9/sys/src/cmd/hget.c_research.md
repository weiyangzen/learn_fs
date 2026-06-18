# File Research: sources/os/plan9/plan9/sys/src/cmd/hget.c

Resumable HTTP/HTTPS/FTP downloader for Plan 9.

- Supports `hget [-dhv] [-o outfile] [-p body] [-x netmtpt] [-r header] url`.
- Parses `http`, `https`, and `ftp` URLs, optional proxy from `httpproxy`, output-file resume offsets, custom request header, and form-urlencoded POST body.
- HTTP path sends HTTP/1.0 requests, supports Range/If-Range resume, redirects, cookies via `/mnt/webcookies/http`, Basic authentication through `auth_getuserpasswd`, response headers, and mtime preservation.
- HTTPS wraps the TCP fd with `tlsClient()`, but explicitly notes certificate checking is missing.
- FTP path supports anonymous login, binary mode, MDTM/SIZE resume checks, REST restart, passive mode first, then active mode fallback.
- Output path tracks offsets and MD5 states to validate already-written resumed bytes before appending new data.

Important structures: `URL`, `Range`, and `Out`. Important helpers include `crackurl`, `dohttp`, `httpheaders`, `doftp`, `ftprestart`, `passive`, `active`, buffered `readline`/`readibuf`, and `output`.

Notable concerns:
- `Range` and output offsets are `long`/`int` in places; comments note only 2 GB range support.
- HTTPS does not verify certificates.
- HTTP proxy support is limited and FTP proxy is marked untested.
- Header parsing and URL parsing are minimal and mutate input URL strings.
