## sources/sync-backup/kopia/internal/auth/authn_test.go

Purpose: tests single-user authentication and authenticator composition.

Important APIs/types/functions: `TestAuthentication`, `TestCombineAuthenticators_Empty`, `TestCombineAuthenticators`, and `verifyAuthenticator`.

Control flow, state, and persistence: constructs authenticators with hard-coded credentials and checks positive and negative combinations. No external state.

Dependencies and integration points: exercises `auth.Authenticator` through public constructors.

Risks and test signals: confirms empty composition returns nil and composed authenticators accept any configured credential set. Does not inspect timing characteristics.
