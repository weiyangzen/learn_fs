# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/fs/http/server/HttpFSAuthenticationFilter.java

## Purpose
`HttpFSAuthenticationFilter` adapts Hadoop delegation-token authentication for the HttpFS gateway by loading authentication and proxy-user configuration from the HttpFS server configuration.

## Important APIs, Types, and Functions
The class extends `DelegationTokenAuthenticationFilter`. `getConfiguration()` builds hadoop-auth properties from `hadoop.http.authentication.*`, then overlays `httpfs.authentication.*`, requires a signature secret file unless a random signer secret provider is already installed, sets the auth handler class, and chooses the WebHDFS or SWebHDFS delegation token kind based on SSL. `getProxyuserConfiguration()` rewrites `httpfs.proxyuser.*` entries into Hadoop proxyuser config. `isRandomSecret()` checks servlet context signer provider state.

## Control Flow
During filter initialization, Hadoop auth calls `getConfiguration()`. The filter reads server config from `HttpFSServerWebApp.get()`, loads the signature secret file as UTF-8 when needed, and returns properties to the parent authentication stack.

## State and Persistence Behavior
No persistent app state is written. It reads the configured signature secret file and constructs in-memory properties. Authentication cookies and delegation tokens are handled by the parent filter stack.

## Dependencies and Integration Points
It integrates with Hadoop auth, delegation token web handlers, HttpFS configuration, servlet filter config/context, and `WebHdfsConstants` token kinds. It depends on `HttpFSServerWebServer.SSL_ENABLED_KEY` to choose secure token kind.

## Risks and Edge Cases
Missing or unreadable signature secret file causes runtime failure. Overlay order means `httpfs.authentication.*` intentionally overrides `hadoop.http.authentication.*`. Random secret detection depends on servlet context attribute and exact class equality with `RandomSignerSecretProvider`.

## Test Signals
No direct tests in this subset. Security integration tests should validate simple/Kerberos modes, proxyuser handling, SSL token kind, and secret file failures.
