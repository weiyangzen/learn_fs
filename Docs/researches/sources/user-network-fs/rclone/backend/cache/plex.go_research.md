# sources/user-network-fs/rclone/backend/cache/plex.go

## Purpose
`plex.go` provides optional Plex integration for the cache backend so read worker behavior can adapt when Plex is actively playing a cached object.

## Important APIs, Types, And Control Flow
The file defines Plex JSON DTOs for play-session notifications and a `plexConnector` holding server URL, credentials/token, TLS mode, owner FS, websocket running state, cached session details, and token persistence callback. `newPlexConnector` validates URL and stores credentials; `newPlexConnectorWithToken` starts websocket listening immediately. `authenticate` posts to Plex login, extracts `user.authToken`, saves it, and starts `listenWebsocket`. The websocket loop receives notifications, fetches details for playing sessions into `stateCache`, and removes stopped sessions. `isPlaying` optionally decrypts a cache object remote through crypt wrapper and searches cached Plex session payloads for the remote path.

## State And Persistence
Runtime state includes websocket connection status, token, and an in-memory expiring cache of Plex session detail payloads. Token persistence is delegated to the callback passed by `NewFs`, which stores `plex_token` into the config mapper. No file storage is directly modified here.

## Dependencies And Integration Points
It depends on `net/http`, `x/net/websocket`, TLS config, `patrickmn/go-cache`, and cache `Fs.isWrappedByCrypt`. `Handle.startReadWorkers` and `confirmExternalReading` query Plex state to choose one worker until playback is confirmed.

## Risks And Test Signals
Risks include no explicit response body close in some HTTP paths, insecure TLS option, substring matching against raw session JSON, websocket reconnect behavior, and token handling. Test coverage is mostly indirect through read-worker behavior; explicit Plex integration tests are absent in this subset.
