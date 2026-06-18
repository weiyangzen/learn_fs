# Research: sources/object-store/minio-mc/cmd/license-register.go

Purpose: implements `mc license register`, registering a MinIO cluster with SUBNET online or generating offline registration URLs.

Important APIs/types/functions: `licenseRegisterFlags`, `licenseRegisterCmd`, `licRegisterMessage`, `ClusterRegistrationReq`, `ClusterRegistrationInfo`, `ClusterInfo`, `SubnetLoginReq`, `SubnetMFAReq`, `isPlay`, `validateNotPlay`, `mainLicenseRegister`, and `getAdminInfo`.

Control flow: validates one target, rejects the public play cluster, optionally reads a license file and saves it, otherwise initializes SUBNET connectivity. It derives cluster name, fetches server info, builds registration info, attempts online registration if not airgapped, marks action registered or updated, and falls back to offline token URL on failure or airgap.

State and persistence: may store license/API key locally through SUBNET helpers and registers/updates cluster state in SUBNET. Reads local license files and server info.

Dependencies/integration points: DNS lookup for play detection, madmin `ServerInfo`, SUBNET registration/token helpers, local config helpers.

Risks: play detection relies on DNS unless airgapped. Online failure falls back to offline URL instead of hard failing. Registration sends cluster inventory/capacity metadata.

Test signals: no direct tests; cover play rejection, license-file path, airgap mode, already registered update, and offline fallback.
