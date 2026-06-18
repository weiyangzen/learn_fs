# sources/object-store/minio/cmd/user-provider-utils.go

Maps credentials and claims to MinIO user-provider identities. `getUserWithProvider` validates or normalizes built-in users and LDAP users/DNs. `guessUserProvider` classifies regular, service, and temp credentials based on LDAP and subject claims plus parent-user provider prefixes. `populateProviderInfoFromClaims` fills `madmin.InfoAccessKeyResp` with LDAP or OpenID-specific details.

The code reads global IAM, LDAP, OpenID, and server config state without persisting changes. OpenID details are resolved by matching role ARN claims to configured providers and then extracting configured display/user ID claims.

Risks include ambiguous parent-user separators, stale global config, missing claims, and provider mismatch error selection. No direct tests in this subset cover it.
