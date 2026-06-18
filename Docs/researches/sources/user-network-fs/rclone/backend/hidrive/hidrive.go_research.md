
# sources/user-network-fs/rclone/backend/hidrive/hidrive.go

## Purpose
This file registers and implements the HiDrive rclone backend. It handles OAuth setup, backend options, object metadata, listing, upload/update, server-side copy/move, directory operations, hash exposure, token renewal, and interface declarations.

## Important APIs, Types, And Control Flow
`init` registers the `hidrive` backend and custom HiDrive hash type. `NewFs` parses options, normalizes root prefix and root, creates an OAuth REST client, configures pacers, validates root prefix, checks whether root is missing, a directory, or a file, and returns `fs.ErrorIsFile` for file roots. `Fs.List` paginates directory entries and constructs `fs.Dir` or `Object` values. `Put` updates existing objects or delegates to `PutUnchecked`; `PutUnchecked` creates an initial file up to the cutoff atomically, creates parents once if needed, and then continues via `Object.Update` with a seek offset. `Copy`, `Move`, and `DirMove` use server-side operations and create destination parents on one retry. `Object` lazily reads metadata, exposes ID, size, modtime, HiDrive hash, range-capable `Open`, metadata patching for modtime, chunked or simple update, and removal.

## State And Persistence
Persistent state is remote HiDrive file and directory contents plus metadata. Object instances cache metadata once loaded. The OAuth token renewer may refresh token state through rclone's OAuth stack. Upload configuration controls whether mutations happen through single create/overwrite calls or non-atomic chunked patch/truncate operations.

## Dependencies And Integration Points
The backend depends on `api` types, `helpers.go`, `hidrivehash`, rclone `fs`, OAuth, rest, pacer, config/encoder, and hash registration. It implements `fs.Fs`, `Purger`, `PutStreamer`, `PutUncheckeder`, `Copier`, `Mover`, `DirMover`, `Shutdowner`, `fs.Object`, and `fs.IDer`.

## Risks And Test Signals
`Shutdown` calls `f.tokenRenewer.Shutdown()` without a nil check; construction paths without a token source would panic. `PutUnchecked` reads up to upload cutoff before object creation and may delete a failed partially uploaded object, but delete failure returns the object with the upload error. Metadata is lazy, so `Size`, `ID`, and `ModTime` use logging fallbacks when API reads fail. Names over 255 characters are noted as provider errors. Tests should cover root prefix validation, root-as-file, chunk cutoff/offset continuation, existing-object update, parent auto-creation, copy/move conflict handling, hash metadata, no-member-count listing, and token renewer behavior.
