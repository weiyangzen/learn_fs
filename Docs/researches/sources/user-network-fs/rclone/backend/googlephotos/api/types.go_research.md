# sources/user-network-fs/rclone/backend/googlephotos/api/types.go

## Purpose
This file defines the JSON payload types used by the Google Photos backend.

## Important APIs, Types, And Control Flow
`ErrorDetails` and `Error` model API failures and implement `error`. Album-related types include `Album`, `ListAlbums`, and `CreateAlbum`. Media listing types include `MediaItem` and `MediaItems`, with embedded media metadata and creation time. Search filter types include `Date`, `DateFilter`, `ContentFilter`, `MediaTypeFilter`, `FeatureFilter`, `Filters`, and `SearchFilter`. Upload commit types include `SimpleMediaItem`, `NewMediaItem`, `BatchCreateRequest`, `BatchCreateResponse`, and `BatchRemoveItems`.

## State And Persistence
There is no local state. The types represent persistent remote Google Photos resources, upload tokens being committed into media items, and filter state sent with list/search requests.

## Dependencies And Integration Points
It depends on `fmt` and `time`. `googlephotos.go` and `pattern.go` use these types for album listing/creation, media searching, upload batch creation, and album item removal.

## Risks And Test Signals
Risks include Google Photos API policy/schema changes, especially app-created-data limitations, upload result status codes, and filter fields. Tests should include JSON fixtures for errors, paged album/media listings, date/feature filters, and batch create responses with per-item failures.
