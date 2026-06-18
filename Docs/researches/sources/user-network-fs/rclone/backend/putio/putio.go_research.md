# sources/user-network-fs/rclone/backend/putio/putio.go

## Purpose
Put.io backend registration: registers OAuth config, constants, ignored system-file regex, options and interface assertions.

## Important APIs, Types, And Functions
Important surface: putioConfig, ignoredFiles, Options, init, interface assertions.

## Control Flow
package init registers backend and config flow; runtime behavior lives in fs.go/object.go/error.go

## State And Persistence
global descriptors and regex only; OAuth persists in rclone config.

## Dependencies And Integration Points
rclone fs/config/oauthutil/obscure/dircache/encoder.

## Risks And Test Signals
Risks and useful test signals: OAuth secret maintenance, NoOffline token behavior, fixed chunk/rate defaults.
