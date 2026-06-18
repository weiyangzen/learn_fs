# sources/user-network-fs/rclone/backend/webdav/odrvcookie/fetch.go

Purpose: fetch SharePoint Online `FedAuth` and `rtFa` cookies for WebDAV authentication using a WS-Trust username/password flow.

Important APIs: `CookieAuth`, `CookieResponse`, XML success/error response structs, `New`, `Cookies`, `getSPCookie`, `getSPTokenURL`, `getSPToken`, and `spTokenURLMap`.

Control flow/state: constructs a SOAP request to the TLD-specific Microsoft STS endpoint, extracts a binary security token, posts it to SharePoint `/_forms/default.aspx?wa=wsignin1.0`, and reads cookies from a cookie jar.

Dependencies/integration: HTTP/XML/template/cookiejar/url, rclone `fs/fshttp`, and publicsuffix. Called by `webdav.setQuirks("sharepoint")`.

Risks/test signals: sensitive to Microsoft auth changes, MFA, endpoint TLD mapping, and response XML shape. No direct unit tests in this subset.
