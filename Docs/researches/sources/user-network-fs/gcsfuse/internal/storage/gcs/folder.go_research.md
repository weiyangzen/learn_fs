# sources/user-network-fs/gcsfuse/internal/storage/gcs/folder.go

## Purpose
This file defines the internal folder DTO used for hierarchical namespace bucket operations and conversion from Storage Control API folder protos.

## Important APIs and Control Flow
`Folder` contains `Name` and `UpdateTime`. `GCSFolder` converts a `controlpb.Folder` into a `*Folder`, extracting the user-visible folder name through `getFolderName` and converting protobuf update time with `AsTime`. `getFolderName` removes the control API prefix `projects/_/buckets/{bucket}/folders/` using `strings.TrimPrefix`.

## State, Dependencies, and Integration
There is no state. Dependencies include `strings`, `time`, and `cloud.google.com/go/storage/control/apiv2/controlpb`. The conversion is used by bucket folder APIs such as get, create, delete, and rename in HNS flows.

## Risks and Test Signals
`strings.TrimPrefix` silently returns the original string if the expected bucket prefix is absent. That is forgiving but can hide malformed control API names. `GCSFolder` assumes `attrs` is non-nil and would panic if passed nil.
