# sources/user-network-fs/rclone/backend/filelu/filelu.go

Purpose: This is the main FileLu rclone backend. It registers configuration, creates HTTP/REST clients, exposes features, and implements root handling, listing, uploads, directory creation/removal, quota, purge, and move-by-copy/delete behavior.

Important APIs and types: `Options` stores API key, encoding, upload cutoff, and chunk size. `Fs` stores name/root/options/features, endpoint, pacer, REST/client handles, and target filename. Key methods include `NewFs`, `Mkdir`, `About`, `Purge`, `List`, `Put`, `Move`, and `Rmdir`.

Control flow: `NewFs` parses config, requires the FileLu key, trims root, builds clients, fills features, and probes root-as-file by temporarily changing root and calling `NewObject`. `List` builds a full API path, calls `getFolderList`, filters nested top-level folders when listing root, strips the backend root from folder paths, and returns `fs.Dir` or lightweight `Object` entries. `Put` delegates to `Object.Update`. `Move` either copies to a local absolute path if the destination looks local, or opens the source, uploads to the destination path, then removes the source. `Rmdir` lists a directory first and refuses to delete if it contains files or folders.

State and persistence behavior: Local state is limited to the root string, options, and cached object fields in listings. Server-side state changes include folder create/delete, upload, purge, and file removal after move. `About` parses provider storage strings into bytes.

Dependencies and integration points: It depends on rclone `fs`, `configstruct`, `fshttp`, `rest`, `pacer`, `encoder`, and helpers in the sibling FileLu files. It advertises empty-directory support, slow hashes, `fs.Purger`, `fs.Abouter`, `fs.Mover`, and `fs.Object`.

Risks: `Move` has surprising local-filesystem behavior for absolute or Windows-looking destinations, which is unusual for a cloud backend. Remote moves are copy/upload/delete, not atomic. Listing uses current time for folder and file modtimes. Root-as-file detection is heuristic. The pacer is a bare `pacer.New()` rather than configured with min/max. Errors from `Mkdir` during multipart parent creation can be ignored in one path.

Test signals: The integration test runs `fstests` against `TestFileLu:` with invalid UTF-8 skipped. There are no local unit tests for path stripping, local-destination moves, or quota parsing.
