# sources/user-network-fs/rclone/lib/oauthutil/oauthutil.go

Source read signal: reviewed complete local file (1122 lines, sha256 d8e824981c71d8c6).

Purpose: Provides OAuth2 configuration, token persistence/refresh, interactive config state-machine flows, local callback server, client-credentials flow, and rc controls for active OAuth setup.

Important APIs/types/functions: Major APIs include `Config`, `MakeOauth2Config`, `MakeClientCredentialsConfig`, `SharedOptions`, `GetToken`, `PutToken`, `TokenSource`, `NewClientWithBaseClient`, `NewClientCredentialsClient`, `NewClient`, `AuthResult`, `Options`, `ConfigOut`, `ConfigOAuth`, rc handlers, `getAuthURL`, `configSetup`, `configExchange`, and `authServer`.

Control flow: Client creation overrides credentials from config, loads tokens, wraps oauth token sources, and saves refreshed tokens. `TokenSource.Token` returns cached valid tokens, rereads config for concurrent refreshes, builds the right oauth token source, retries refresh, wraps fatal OAuth errors, updates expiry timers, and persists changed tokens. `ConfigOAuth` is a state machine for existing-token confirmation, local/remote browser choice, authorize-token paste, client-credentials direct token retrieval, local webserver callback, and final return state. The auth server validates state, redirects `/auth` to the provider URL, receives callback data at `/`, renders a success/failure template, and sends an `AuthResult`.

State and persistence behavior: Persists OAuth tokens in the config mapper as JSON. Maintains process-global OAuth cancel function and active auth URL for rc status/stop. Token sources hold cached tokens, timers, and mutexes. Local auth server opens a TCP listener on 127.0.0.1:53682.

Dependencies and integration points: Uses `oauth2`, `clientcredentials`, rclone config/fserrors/fshttp/rc/random, `open-golang`, and HTTP/template packages. Backends register OAuth options and delegate config to `fs.ConfigOAuth`.

Risks and test signals: The flow has security-sensitive state validation and proxy/browser behavior. Global `templateString`, `oauthCancelFn`, and fixed port can conflict with concurrent auth attempts. Token refresh handles fatal OAuth errors specially. Some copied source lines show duplicated `if` text, so compile/test status should be watched. rc tests cover status/stop only.
