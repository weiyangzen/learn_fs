
# sources/user-network-fs/rclone/backend/huaweidrive/api/types.go

## Purpose
This file defines Huawei Drive API request and response structures, constants, regional endpoint mappings, and small helpers used by the backend.

## Important APIs, Types, And Control Flow
`About`, `User`, `FileList`, and `File` model quota, account, listing, and file/folder metadata responses. `File.IsDir` checks the Huawei folder MIME type. Request types include `CreateFolderRequest`, `UpdateFileRequest`, and `CopyFileRequest`. Upload/change types include `ResumeUploadInitResponse`, `StartCursor`, `ChangeList`, and `ChangeItem`. Constants define MIME types, upload/form types, categories, and global API roots. `DomainToRootURL` maps provider domain names/regions to regional API roots; `GlobalDomains` marks domains that should not be switched. `BoolPtr` supports optional boolean update fields.

## State And Persistence
The file contains only DTOs and static maps. It does not perform persistence. The regional maps influence runtime endpoint selection in `huaweidrive.go`.

## Dependencies And Integration Points
The backend uses these types for all REST calls: about/quota, file listing, folder creation, metadata update, copy, resumable upload initialization, errors, and change notification.

## Risks And Test Signals
Many numeric API values are strings in `About` and must be parsed by callers. Metadata maps use `map[string]interface{}`, so type conversion is caller-controlled. Regional domain coverage must stay aligned with Huawei responses. Tests should verify `IsDir`, endpoint-domain switching values, bool pointer behavior, and JSON compatibility for update/create/copy/upload/change payloads.
