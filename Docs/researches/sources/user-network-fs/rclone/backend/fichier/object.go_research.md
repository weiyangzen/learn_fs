# sources/user-network-fs/rclone/backend/fichier/object.go

Purpose: This file implements the 1Fichier `Object` side of rclone's object interface: metadata access, hash, open/download, update, remove, MIME type, and ID.

Important APIs and types: `Object` contains `fs`, `remote`, and a cached `File` DTO. Methods include `String`, `Remote`, `ModTime`, `Size`, `Fs`, `Hash`, `Storable`, `SetModTime`, `setMetaData`, `Open`, `Update`, `Remove`, `MimeType`, and `ID`.

Control flow: `Open` fixes range options against the known size, obtains a download token for the object's URL, then makes a GET request to the token URL with open options. `Update` rejects unknown sizes, uploads a duplicate object through `putUnchecked`, deletes the old object only after the upload succeeds, then replaces the receiver with the new object. `Hash` supports only Whirlpool and returns the stored checksum. `ModTime` parses the provider date string and falls back to current time on parse failure.

State and persistence behavior: Object metadata is cached in the `file` field and replaced after update. Provider state changes happen through duplicate upload plus old-object deletion, or direct deletion via file URL. Modtime cannot be changed server-side.

Dependencies and integration points: It uses helpers from `api.go`, DTOs from `structs.go`, rclone `fs.Object`, `fs.MimeTyper`, `fs.IDer`, `hash.Whirlpool`, and `rest` for downloads.

Risks: Updating a file is not atomic: a successful upload followed by failed delete leaves duplicates. Unknown-size updates are refused. Modtime parsing depends on `2006-01-02 15:04:05`. Range support depends on `rest` open option handling and the 1Fichier token URL. `SetModTime` is unsupported.

Test signals: Generic `fstests` exercise object read/write/remove/hash/MIME behavior through `fichier_test.go`.
