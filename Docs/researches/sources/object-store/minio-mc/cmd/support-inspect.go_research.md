<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-inspect.go -->
# sources/object-store/minio-mc/cmd/support-inspect.go

Purpose: implements `mc support inspect`, which downloads raw object/metadata inspection data from MinIO, optionally encrypts it with a public key, and either uploads it to SUBNET or saves it for airgapped/manual sharing.

Important APIs/types/functions: `supportInspectCmd`, `supportInspectFlags`, `inspectMessage`, `mainSupportInspect`, and `saveInspectDataFile` define CLI, output, admin-client interaction, stream validation, upload, and local persistence.

Control flow: the command validates a single target, initializes SUBNET connectivity and registration, creates an admin client, parses alias/bucket/prefix, warns when shell wildcard support is likely missing, loads `support_public.pem` from the mc config directory or falls back to `defaultPublicKey`, then calls `client.Inspect`. If the server did not return an encryption key, the response is piped through `estream.NewReader` to validate stream structure while simultaneously writing to a temp file. Airgapped mode moves the temp file to a stable inspect filename. Online mode uploads with `SubnetFileUploader`; if upload fails, it saves locally instead.

State and persistence: writes temporary `mc-inspect-*` files, final `inspect-...enc` or `inspect-data.<crc>.enc` files, and rotates an existing final file with a timestamp suffix. The returned decryption key is printed only once for locally saved encrypted data.

Dependencies and integration points: depends on MinIO admin inspect API, `madmin.InspectOptions`, `madmin-go/estream`, SUBNET upload helpers, config-dir helpers, shell detection, and shared `moveFile` from support profile code.

Risks and test signals: sensitive-data handling and one-time key display are critical. Tests should cover public key override, legacy mode, stream validation failures, upload fallback, existing-file rotation, wildcard shell warnings, and airgapped output.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-inspect.go -->
