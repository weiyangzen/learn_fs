# Research: sources/object-store/minio-mc/cmd/license-unregister.go

Purpose: implements hidden `mc license unregister`, unregistering a cluster from SUBNET and removing local auth config.

Important APIs/types/functions: `licenseUnregisterCmd`, `licUnregisterMessage`, `checkLicenseUnregisterSyntax`, and `mainLicenseUnregister`.

Control flow: validates one target, initializes SUBNET connectivity, obtains or validates API key, calls SUBNET unregister with deployment ID unless airgapped, removes local SUBNET auth config, and prints success.

State and persistence: mutates SUBNET registration state online and deletes local SUBNET auth/config for the alias.

Dependencies/integration points: SUBNET helpers, `getAdminInfo`, local config removal.

Risks: hidden but destructive for support registration. In airgapped mode it only removes local config, not remote SUBNET state.

Test signals: no direct tests; cover registered/unregistered aliases, airgap, API key flag, and local config removal.
