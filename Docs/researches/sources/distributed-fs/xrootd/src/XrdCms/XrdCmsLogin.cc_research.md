# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsLogin.cc

Purpose: implements the CMS login handshake between cmsd peers/managers and clients, including packed login exchange, optional security challenge/response, blacklist rejection/redirect, and login error handling.

Important APIs/types/functions: `XrdCmsLogin::Admit()`, static `Login()`, `sendData()`, `Emsg()`, and blacklist helpers `SendErrorBL()`.

Control flow: `Admit()` reads the full request with `XrdCmsTalk::Attend`, authenticates if a token is configured, initializes response login data, parses the incoming login payload through `Parser.Parse`, checks blacklist status for non-directors, fills SID/env CGI for compatible versions, and sends a packed login response. `Login()` sets the blacklist-redirect capability, sends packed login data, clears outbound pointer fields, receives a response header/body, handles `kYR_xauth` by identifying through `XrdCmsSecurity`, handles `kYR_try` redirects by unpacking hosts into `Data.Paths`, handles `kYR_error`, and parses normal login data. `sendData()` packs login fields into iovecs and splits sends around `IOV_MAX`.

State and persistence behavior: state is per-handshake. Returned `SID`, `envCGI`, and redirect path strings are duplicated for caller ownership. Login mode bits and protocol version affect cross-version persistent compatibility.

Dependencies: `XrdLink`, `YProtocol.hh`, `XrdCmsParser`, `XrdCmsTalk`, `XrdCmsSecurity`, `XrdCmsBlackList`, `XrdOucPup`, network byte-order helpers, and CMS logging.

Integration points: used by manager/client connection setup (`XrdCmsClientMan`) and server admission paths. Blacklist redirects can trigger manager rerouting and permanent topology changes.

Risks: fixed 4096-byte login response buffer rejects larger replies. Error handling returns a mix of CMS error codes, `-1`, and `kYR_EINVAL`, so callers must interpret carefully. Packed pointer fields are manually cleared/duplicated. Security depends on external token/identify functions. `sendData()` ignores the return value of `Link->Send()`.

Test signals: successful login parse/pack round trip, xauth challenge, blacklist hard error, blacklist redirect, malformed try host data, oversized replies, IOV splitting, and version compatibility with/without SID/env CGI.
