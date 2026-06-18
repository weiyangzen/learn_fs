# sources/user-network-fs/rclone/backend/cloudinary/api/types.go

## Purpose
This file defines small shared API types for the Cloudinary backend: an encoder extension interface and an update option passed from object update paths into put/upload logic.

## Important APIs, Types, And Control Flow
`CloudinaryEncoder` extends standard path/name encoding with `FromStandardFullPath`, allowing the backend to encode a full root-relative Cloudinary path. `UpdateOptions` carries `PublicID`, `ResourceType`, `DeliveryType`, `AssetFolder`, and `DisplayName`. It implements rclone's open-option style methods: `Header` returns key `"UpdateOption"` with a `resource/delivery/publicID` value, `Mandatory` returns false so unaware consumers can ignore it, and `String` formats a human-readable fully qualified public ID.

## State And Persistence
The file stores no state. `UpdateOptions` is a value object used to preserve Cloudinary identity metadata across an update-to-put handoff.

## Dependencies And Integration Points
It depends only on `fmt`. The option type integrates with Cloudinary backend upload/update code and rclone's generic option plumbing through `Header`, `Mandatory`, and `String` conventions.

## Risks And Test Signals
Risks are semantic rather than algorithmic: `Header` omits asset folder and display name, so consumers must get those fields by type assertion rather than header text; `Mandatory` being false means the option can be silently ignored by non-Cloudinary paths. Test signals should verify update preserves resource type, delivery type, public ID, asset folder, and display name where relevant.
