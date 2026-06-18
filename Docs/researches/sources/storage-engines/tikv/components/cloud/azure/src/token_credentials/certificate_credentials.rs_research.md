# sources/storage-engines/tikv/components/cloud/azure/src/token_credentials/certificate_credentials.rs

## Purpose
Provides a stable local implementation of Azure client-certificate token credentials. It builds a JWT client assertion from a base64 PKCS#12 certificate and exchanges it with Azure AD for an `AccessToken`.

## Important APIs, Types, And Functions
- `ClientCertificateCredentialExt` implements `azure_core::auth::TokenCredential`.
- `new` accepts tenant ID, client ID, base64 PKCS#12 certificate, and password.
- `build` reads a certificate file and base64-encodes it before construction.
- `CertificateCredentialOptions` supplies authority host and `send_certificate_chain`; defaults to Azure public login and sends x5c.
- `sign`, `get_thumbprint`, and `as_jwt_part` build the signed JWT assertion.
- `get_token` decodes PKCS#12, extracts cert/private key, creates and signs JWT, posts form-encoded client-credentials data, parses `AadTokenResponse`, and returns `AccessToken`.

## Control Flow
Every `get_token` call reparses the PKCS#12 certificate, computes SHA-1 thumbprint, builds a JWT expiring in 300 seconds, and posts to `{authority}/{tenant}/oauth2/v2.0/token`. HTTP failures are converted with Azure core helpers; JSON success bodies provide `access_token` and `expires_in`.

## State And Persistence Behavior
The struct stores certificate material and password in memory. `clear_cache` is a no-op and this implementation does not cache tokens internally; higher-level callers such as Azure Blob token builders cache if needed.

## Dependencies And Integration Points
Uses `openssl`, `azure_core`, `serde`, `time`, and `url::form_urlencoded`. Azure KMS consumes this credential for certificate-based authentication.

## Risks And Edge Cases
Certificate and password are stored as plain `String`s and derived `Debug` can expose fields if logged. Repeated token requests reparse the certificate. `ext_expires_in` and `token_type` are parsed but not validated. x5c and base64 formatting must remain Azure AD compatible.

## Test Signals
No local tests. Coverage is indirect through Azure KMS construction; no active tests cover JWT construction, x5c chain handling, password-protected certificates, or HTTP error handling.
