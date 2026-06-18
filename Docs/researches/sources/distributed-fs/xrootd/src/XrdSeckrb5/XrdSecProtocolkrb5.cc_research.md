# sources/distributed-fs/xrootd/src/XrdSeckrb5/XrdSecProtocolkrb5.cc

## Purpose
`XrdSecProtocolkrb5.cc` implements the Kerberos 5 XRootD security protocol plugin. It supports client-side AP-REQ credential generation, server-side AP-REQ validation against a service principal and keytab, optional IP address checking, and optional forwarding/export of delegated Kerberos credentials into a server-side credential cache file.

## Important APIs, types, and functions
The central class is `XrdSecProtocolkrb5 : public XrdSecProtocol`. Public protocol methods are `getCredentials()` for clients and `Authenticate()` for servers. Static initialization and configuration are handled by `Init()`, `setOpts()`, `setClientOpts()`, `setParms()`, and `setExpFile()`. Private helpers include `Fatal()`, `get_krbCreds()`, `get_krbFwdCreds()`, `exp_krbTkn()`, and `SetAddr()`.

The required plugin exports are `XrdSecProtocolkrb5Init()` and `XrdSecProtocolkrb5Object()`, plus `XrdVERSIONINFO(XrdSecProtocolkrb5Object,seckrb5)`. The protocol identifier embedded in credential buffers is `"krb5"`.

## Control flow
On server initialization, `XrdSecProtocolkrb5Init('s', parms, erp)` parses optional keytab path, `-ipchk`, `-exptkn[:template]`, and the service principal. `<host>` in the principal is expanded to the local hostname. `Init()` creates a Kerberos context, opens the default credential cache and keytab, checks that the keytab can be read, parses the service principal, and returns parameters containing the principal plus `,fwd` when forwarding is requested.

On client initialization, the init function sets debug and `kinit` retry options from environment variables and defers most context/cache setup to `getCredentials()`. `XrdSecProtocolkrb5Object()` creates per-connection protocol objects. Clients take the target principal from server parameters; servers use the already initialized static context.

Client `getCredentials()` locates a credential cache from `xrd.k5ccname`, `KRB5CCNAME`, or `/tmp/krb5cc_<euid>`, initializes a client context, opens the cache, strips a `,fwd` suffix from the service when present, obtains service credentials, optionally runs `kinit` or `kinit -f` when configured and interactive, creates an auth context, and serializes a Kerberos request after the `"krb5"` prefix. If the handshake has already advanced and forwarding is enabled, it calls `get_krbFwdCreds()` and returns the forwarded credential blob.

Server `Authenticate()` validates the prefix, handles the second-step forwarded credential by calling `exp_krbTkn()`, and otherwise reads the AP-REQ using `krb5_rd_req()`. Unless `XrdSecNOIPCHK` is set, it binds the auth context to the peer address. Successful authentication maps the Kerberos principal to a local name with `krb5_aname_to_localname()` and stores it in `Entity.name`. If forwarding is enabled, it returns `kpST_more` semantics by setting `*parms` to a fake `fwdtgt` parameter buffer and expecting a second credential packet.

## State and persistence behavior
Static state includes server and client Kerberos contexts, credential caches, the keytab, parsed server principal, exported parameter string, option flags, and the forwarding export filename template. Per-object state includes endpoint address, service principal, step counter, auth contexts, ticket, credentials, and the mapped client name.

Persistent side effects occur only when delegated credentials are exported. `exp_krbTkn()` expands `<user>` and `<uid>` in the `ExpFile` template, reads forwarded credentials with `krb5_rd_cred()`, resolves and initializes a credential cache at that path, stores the credential, closes the cache, and chmods the file to `0600`.

## Dependencies and integration points
The plugin depends on MIT/Heimdal Kerberos APIs, com_err, XRootD network endpoint abstractions, `XrdOucErrInfo`, `XrdOucTokenizer`, `XrdSysMutex`, `XrdSysPwd`, and the `XrdSecInterface` plugin ABI. It integrates with XRootD by exporting protocol init/object constructors that the security loader calls.

## Risks and edge cases
The Kerberos contexts and caches are static and protected by broad mutexes, which reduces concurrency risk but serializes credential operations. `exp_krbTkn()` has several early returns while holding `krbContext.Lock()`, so errors in that path can leave the mutex locked. The `<uid>` expansion path uses `memmove(puid+ln, pusr+5, lm)` where `pusr` may be null or unrelated to the `<uid>` placeholder, which is a suspicious buffer manipulation bug. `Parms` is static but freed in each object's `Delete()`, so multiple objects can race or double-free shared parameters. Invoking `system("kinit")` from the client path depends on an interactive terminal and external command availability. IP checking defaults to disabled in init options unless `-ipchk` is supplied.

## Test signals
Coverage should include plugin initialization with valid and invalid principals/keytabs, client credential generation from `KRB5CCNAME` and `xrd.k5ccname`, AP-REQ validation success and failure, local-name mapping failures, `-ipchk` address mismatch, forwarding requested by `-exptkn`, exported cache permissions, and non-interactive behavior when no valid ticket exists. Static analysis should flag the forwarding export error-unlock paths and the `<uid>` template buffer code.
