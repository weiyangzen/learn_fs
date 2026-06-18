# sources/user-network-fs/rclone/backend/drime/api/types.go

Purpose: Defines Drime API request and response models for listing, metadata, CRUD operations, uploads, multipart upload lifecycle, and quota.

Important APIs, types, and functions: `Item` is the central file/folder metadata type, with `User` and `Permissions` nested details. Listing and upload types include `Listing`, `UploadResponse`, `CreateFolderRequest/Response`, `DeleteRequest/Response`, `UpdateItemRequest/Response`, `MoveRequest/Response`, `CopyRequest/Response`, multipart create/sign/complete/entry/abort types, and `SpaceUsageResponse`. `Error` implements Go's `error` interface.

Control flow: This file is mostly data definitions. `Error.Error` formats Drime API error messages. All other structs are populated or marshaled by `drime.go` REST calls.

State and persistence behavior: Structs are transient API payloads. Persistent state lives in Drime; runtime state is copied into `Object` metadata and `drimeChunkWriter` upload state.

Dependencies and integration points: Uses `encoding/json` for `json.Number`, `fmt`, and `time`. JSON tags are the contract between `drime.go` and the Drime API.

Risks: Many fields are `any`, so type safety is limited for rarely used metadata. Numeric IDs rely on `json.Number.String()`. API schema drift can break listing, uploads, moves, or quota without compile-time detection.

Test signals: No direct unit tests exist; `drime_test.go` runs integration fstests against a real configured Drime remote.
