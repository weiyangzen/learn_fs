# sources/sync-backup/git-lfs/lfsapi/auth.go

Purpose: Implements authenticated LFS API request execution, credential selection, access-mode upgrades after challenges, and request Authorization header population.

Important APIs/types/functions: `DoWithAuth`, `DoWithAuthNoRetry`, `DoAPIRequestWithAuth`, `doWithAuth`, `doWithCreds`, `getCreds`, `getCredURLForAPI`, `fixSchemelessURL`, `requestHasAuth`, `setRequestAuth*`, `getReqOperation`, and `getAuthAccess`.

Control flow: `DoWithAuth` retries auth failures up to a mode-sensitive limit, closing failed bodies and refreshing access mode after challenges. `doWithAuth` applies extra headers, fills credentials, executes with creds, rejects or approves helper credentials, and stores multistage auth state headers. `doWithCreds` delegates Negotiate to Kerberos/SPNEGO handling, otherwise uses `lfshttp.Client.DoWithRedirect` and recursively reauthenticates redirected requests.

State and persistence behavior: Mutates request headers, endpoint access cache/config through `Endpoints.SetAccess`, credential-helper state fields, and `c.access` mode ordering. It can approve/reject credentials in configured helpers, which may persist outside process depending on helper.

Dependencies and integration points: Integrates `creds`, `lfshttp`, endpoint discovery, Git credential helpers, URL auth, netrc-like credential filling through helper wrappers, and HTTP response error classification.

Risks and edge cases: Existing Authorization or token query suppresses credential filling. Requests to a different scheme/host use request URL credentials rather than endpoint credentials. Multistage auth avoids rejecting creds between stages. Retry limit behavior is critical to avoid loops.

Test signals: `auth_test.go` covers basic/negotiate challenge parsing, approve/reject flows, no-retry mode, retry limit, multistage non-advancement, credential URL derivation, URL embedded auth, remote URL auth, mismatched scheme/host/port, and redirect reauthentication.
