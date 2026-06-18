<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-register.go -->
# sources/object-store/minio-mc/cmd/support-register.go

Purpose: preserves the old `mc support register` command as a deprecated wrapper pointing users to `mc license register`.

Important APIs/types/functions: `supportRegisterFlags`, `supportRegisterCmd`, and `mainSupportRegister`.

Control flow: the command definition still exposes the old name and flags/template, but its action immediately calls `deprecatedError("mc license register")`.

State and persistence: no state is read or written by this deprecated path.

Dependencies and integration points: remains listed under `supportSubcommands` for compatibility and uses shared `subnetCommonFlags`.

Risks and test signals: compatibility risk is in preserving the command while clearly directing users to the replacement. Tests should assert invocation fails or exits with the expected deprecation messaging and does not attempt registration side effects.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-register.go -->
