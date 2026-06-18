# sources/user-network-fs/rclone/cmd/selfupdate/selfupdate.go

Purpose: implements `rclone selfupdate`, downloading and installing a newer rclone binary or Linux package.

Important APIs/types: `Options`, global `Opt`, Cobra `cmdSelfUpdate`, `GetVersion`, `InstallUpdate`, `installPackage`, `replaceExecutable`, `makeRandomExeName`, `downloadUpdate`, `verifyAccess`, `findFileHash`, `extractZipToFile`, and `downloadFile`.

Control flow: command validates package/check/root/platform constraints, then `InstallUpdate` rejects conflicting beta/stable flags and static cmount capability loss, resolves target version/site, handles check-only, package install, output path, temp names, access checks, download, hash verification for stable releases, zip extraction, and executable replacement. Windows replacement saves the running executable as `.old.exe` or randomized old name.

State/persistence: writes temp files, replaces target executable or installs packages with `dpkg/rpm`, makes network requests to rclone download sites, and may leave old Windows executable. Dependencies include fshttp, buildinfo, random, version command, cmount capability, zip/sha256. Risks include self-replacement failure, permissions, network/hash availability, beta lacking hash verification, package install side effects, and platform-specific executable locking. Tests cover version parsing, Linux output install, permissions/temp cleanup, and Windows rename behavior but are marked unreliable.
