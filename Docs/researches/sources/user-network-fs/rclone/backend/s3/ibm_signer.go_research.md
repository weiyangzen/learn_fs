# sources/user-network-fs/rclone/backend/s3/ibm_signer.go

## Purpose
IBM IAM S3 signer: signs IBM COS requests with IAM bearer token headers instead of normal SigV4 credentials.

## Important APIs, Types, And Functions
Important surface: Authenticator, IbmIamSigner, SignHTTP, NoOpCredentialsProvider.

## Control Flow
SignHTTP gets a token from injected or IBM SDK authenticator, sets Authorization and ibm-service-instance-id; no-op provider satisfies AWS SDK credential requirement

## State And Persistence
no local persistence; authenticator may cache tokens.

## Dependencies And Integration Points
IBM go-sdk-core and AWS SDK v2 signer/credentials.

## Risks And Test Signals
Risks and useful test signals: token fetch per sign, ignored SigV4 params, empty instance ID, placeholder creds.
