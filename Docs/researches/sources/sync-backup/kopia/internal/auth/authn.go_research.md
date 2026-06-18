## sources/sync-backup/kopia/internal/auth/authn.go

Purpose: authentication abstraction and implementations for single-user credentials, composed authenticators, and htpasswd files.

Important APIs/types/functions: `Authenticator`, `AuthenticateSingleUser`, `CombineAuthenticators`, `AuthenticateHtpasswdFile`, `singleUserAuthenticator`, `combinedAuthenticator`, and `htpasswdAuthenticator`.

Control flow, state, and persistence: single-user auth stores expected username/password bytes and compares both with `subtle.ConstantTimeCompare`. Combined auth returns true on the first authenticator accepting credentials and refreshes all authenticators in order. htpasswd auth delegates matching and reload to the external `htpasswd.File`.

Dependencies and integration points: used by API/server authentication flows and repository-based authentication in companion files.

Risks and test signals: length-dependent behavior still exists in Go constant-time compare, but username and password comparisons avoid ordinary string equality. Tests cover accepted/rejected credentials and combining behavior.
