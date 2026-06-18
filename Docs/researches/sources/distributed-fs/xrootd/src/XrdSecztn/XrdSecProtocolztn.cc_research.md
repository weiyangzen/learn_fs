# sources/distributed-fs/xrootd/src/XrdSecztn/XrdSecProtocolztn.cc

## Purpose
Implements the `ztn` XRootD security protocol for bearer/SciTokens-style token authentication. It provides the client-side credential collector, the server-side token validator, and the plugin entry points `XrdSecProtocolztnInit` and `XrdSecProtocolztnObject`. The protocol is explicitly TLS-only and exchanges a compact private credential frame containing either a token request opcode or a token payload.

## Important APIs, Types, And Functions
- `XrdSecProtocolztn : XrdSecProtocol` implements `getCredentials()`, `Authenticate()`, `needTLS()`, and `Delete()`.
- `TokenHdr` is the on-wire header with id `"ztn"`, protocol version, opcode, and reserved bytes. Opcodes are `SndAI` for authorized issuer requests and `IsTkn` for token responses.
- `TokenResp` extends `TokenHdr` with a network-order token length and a null-terminated token payload.
- `XrdSecProtocolztnInit()` parses server configuration and returns the client parameter string `TLS:<opts>:<maxtsz>:` after optional token library linkage.
- `XrdSecProtocolztnObject()` constructs client or server protocol objects and rejects non-TLS endpoints.
- `getLinkage()` uses `XrdOucPinLoader` to resolve the external `SciTokensHelper` symbol from `libXrdAccSciTokens.so` or a configured token library.
- `findToken()`, `readToken()`, `Strip()`, and `retToken()` implement client-side token discovery and response framing.

## Control Flow
Server initialization parses `-maxsz`, `-expiry`, and `-tokenlib`. Unless `-tokenlib none` is supplied, it loads the token helper plugin and records the helper linkage pointer. `XrdSecProtocolztnObject()` later dereferences that linkage for server instances, while client instances parse server parameters to learn the maximum token size and option/version field.

Client credential creation first handles continuation state. On the first call it searches default token locations in order: `BEARER_TOKEN`, `BEARER_TOKEN_FILE`, `XDG_RUNTIME_DIR/bt_u<uid>`, `/tmp/bt_u<uid>`, and the `xrd.ztn` URL/environment value. File paths are read, permission-checked, stripped of surrounding whitespace, optionally JWT-header-validated, and packed into `TokenResp`. Runtime token fetch support is advertised in the structure but currently ends in `ENOTSUP` if continuation reaches `getToken()`.

Server authentication validates frame size, protocol id, opcode, version, token length, and null termination. It handles `SndAI` through `SendAI()`, which is currently unsupported. For token frames, it optionally calls `XrdSciTokensHelper::Validate()` to populate `Entity`. Depending on expiry mode it rejects missing or expired expiry values. If token validation is disabled or succeeds, it stores the token in `Entity.creds`, ensures `Entity.name` exists, and returns success.

## State And Persistence
Process-global state includes `MaxTokSize`, `expiry`, `tokenlib`, `sth_Linkage`, and `sth_piName`. Protocol instances hold endpoint identity, token-search state, feature options, continuation state, and the `XrdSciTokensHelper` pointer. No token cache is persisted by this file. On the client, token contents are read from environment variables, token files, or URL environment and sent per authentication attempt. Server-side token bytes are copied into `Entity.creds` for downstream authorization.

## Dependencies And Integration Points
Depends on XRootD security interfaces, `XrdOucErrInfo`, `XrdOucTokenizer`, `XrdOucPinLoader`, `XrdNetAddrInfo`, and `XrdSciTokensHelper`. It integrates as an XRootD security plugin through version metadata and C entry points. It relies on `XrdSecztn::isJWT()` from `XrdSecztn.cc` for lightweight JWT header filtering when enabled. It requires TLS via `endPoint.isUsingTLS()`.

## Risks And Edge Cases
- The expiry check compares `monotonic_time()` to token expiry, but token expiry is normally wall-clock epoch time. This should be audited because monotonic time and epoch time are different domains.
- `-expiry` parsing uses `strcmp(val, "ignore")` style tests in a way that appears inverted: nonzero `strcmp` selects the branch. Tests should catch intended values.
- The protocol says runtime token creation may be requested, but `getToken()` and `SendAI()` are unsupported.
- Token file permission checks happen after reading. That limits use of the returned token, but still reads overly permissive files.
- `Strip()` rejects one-character tokens due to `k <= j`, likely acceptable for real JWTs but notable for generic bearer tokens.
- `retToken()` allocates `sizeof(TokenResp) + tsz + 1`; since `TokenResp` already contains `tkn[1]`, this over-allocates by one, which is safe but imprecise.

## Test Signals
Useful tests include plugin init parameter parsing for all `-expiry` modes, TLS rejection, oversized token rejection, token discovery order, unreadable/missing file behavior, permission failure, JWT header filtering, malformed frame rejection, tokenlib-disabled success path, tokenlib validation failure propagation, and server behavior when the helper linkage has not been initialized.
