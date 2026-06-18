# File Research: sources/os/plan9/plan9/sys/src/cmd/webfs/http.c

This file implements HTTP and HTTPS URL scheme handling for `webfs`.

HTTP state:
- `HttpState` stores fd, client pointer, redirect location, accumulated set-cookie headers, network address, Basic auth credentials, auth error text, and `Ibuf`.

Header handlers:
- `Location:` sets redirect location.
- `Content-Type:` updates client content type.
- `Set-Cookie:` appends normalized header text to `hs->setcookie`.
- `WWW-Authenticate:` handles Basic auth challenge.

Authentication:
- `wwwauthenticate` supports Basic only.
- Uses URL user/pass if present; otherwise asks factotum via `auth_getuserpasswd` with server and realm.
- Encodes `user:pass` using base64 and stores `Authorization: Basic ...`.

Open/request:
- `httpopen` dials `url->host` using URL port or scheme service; HTTPS wraps with TLS through `iotlsdial`.
- Sends HTTP/1.0 GET or POST, Host, optional User-Agent, cookies, post content headers/body, and optional Authorization.
- Parses status line with `httprcode`.
- Handles redirects 301/302/303/307, auth 401, success 200/201/202/204/205/304, and many error status codes.
- Parses MIME headers after status handling.
- Stores accepted cookies via `httpsetcookie`.
- Sets `c->redirect` or `c->authenticate` for caller-driven retry.

Read/close:
- `httpread` reads response body through `readibuf`.
- `httpclose` closes fd via client `Ioproc` and frees all `HttpState` allocations.

Notable risks:
- TLS certificate validation is explicitly missing in the lower-level dial path.
- HTTP/1.0 is used; no chunked-transfer decoding is present.
- Unknown response codes are treated as errors instead of class-based handling.
