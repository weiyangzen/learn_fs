<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-profile.go -->
# sources/object-store/minio-mc/cmd/support-profile.go

Purpose: implements `mc support profile`, collecting MinIO server profiling data and uploading it to SUBNET or saving it locally.

Important APIs/types/functions: `profileFlags`, `supportProfileMessage`, `supportProfileCmd`, `checkAdminProfileSyntax`, `moveFile`, `saveProfileFile`, `mainSupportProfile`, and `execSupportProfile`.

Control flow: syntax validation enforces one target, duration >= 1 second, and profiler types from the `madmin.Profiler*` set. The command initializes SUBNET connectivity and registration, creates an admin client, optionally precomputes upload URL/headers, calls `client.Profile`, saves the returned zip stream to `profile.zip`, then uploads it unless airgapped. Upload failure is reported as an error status while retaining the local file.

State and persistence: writes a temporary profile file, rotates existing `profile.zip` to `profile.zip.<timestamp>`, and moves the new data into `profile.zip`. `moveFile` copies then removes to work across filesystems.

Dependencies and integration points: depends on MinIO admin profiling API, SUBNET upload helpers, shared registration/airgap/global JSON handling, and console message plumbing.

Risks and test signals: profile files may contain sensitive operational data. Tests should cover profiler validation, duration validation, cross-device move fallback, existing-file rotation, upload failure output, and airgapped persistence.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-profile.go -->
