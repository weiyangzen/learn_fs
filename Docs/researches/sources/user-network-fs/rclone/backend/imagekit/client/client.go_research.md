# sources/user-network-fs/rclone/backend/imagekit/client/client.go

## Purpose
Defines the ImageKit API client constructor and shared client configuration used by the ImageKit rclone backend.

## Important APIs, Types, and Functions
`ImageKit` stores API/upload prefixes, timeout values, private/public keys, URL endpoint, and a `rest.Client`. `NewParams` carries required private key, public key, and URL endpoint. `New` validates inputs, creates an rclone HTTP client, sets the `rclone/imagekit` user agent, configures Basic Auth with private key and blank password, sets JSON accept headers, and returns an initialized `ImageKit`.

## Control Flow
`New` reads values from `NewParams`, rejects empty values, applies rclone HTTP config with `fs.AddConfig`, creates a `rest.Client`, and fills constants for `https://api.imagekit.io/v2` and `https://upload.imagekit.io/api/v2`.

## State and Persistence
No persistent state is written. Credentials live in the client object and HTTP Basic Auth state.

## Dependencies and Integration Points
Depends on rclone `fs`, `fshttp`, and `lib/rest`. The backend uses this constructor in `imagekit.NewFs`.

## Risks and Edge Cases
The validation error messages appear swapped: an empty private key reports that the URL endpoint is required, and an empty endpoint reports that the private key is required. Timeout fields are stored but not applied in this file. Public key is stored but not used by the shown client methods.

## Test Signals
There are no unit tests for `client.New`; integration testing is indirect through the ImageKit backend.
