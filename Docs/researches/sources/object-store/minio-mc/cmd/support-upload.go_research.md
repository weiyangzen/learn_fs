<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-upload.go -->
# sources/object-store/minio-mc/cmd/support-upload.go

Purpose: implements `mc support upload`, uploading a local file to a SUBNET issue with optional comment and encryption.

Important APIs/types/functions: `uploadFlags`, `supportUploadMessage`, `supportUploadCmd`, `checkSupportUploadSyntax`, `mainSupportUpload`, and `execSupportUpload`.

Control flow: the command requires `ALIAS FILE` and a positive `--issue`. It initializes SUBNET connectivity/registration, builds URL parameters for issue number and optional comment, prepares the attachment upload URL, and invokes `SubnetFileUploader` with auto-compression and optional auto-encryption. Success output includes the issue URL.

State and persistence: reads a local file and uploads it; does not mutate MinIO cluster config. The uploader may create transient compressed/encrypted artifacts depending on implementation.

Dependencies and integration points: depends on SUBNET URL/auth helpers, `SubnetFileUploader`, support registration/dev mode, global output handling, and URL query encoding.

Risks and test signals: validates issue number but not local file existence directly before uploader call. Tests should cover syntax, issue validation, comment parameter encoding, encryption flag propagation, upload errors, and JSON/text output.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-upload.go -->
