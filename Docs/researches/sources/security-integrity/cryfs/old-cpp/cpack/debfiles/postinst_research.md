# sources/security-integrity/cryfs/old-cpp/cpack/debfiles/postinst

Purpose: Debian post-install maintainer script that adds the CryFS APT repository and package signing key after installing the `.deb`.

Important APIs and types: Functions include `containsElement` (unused), `get_repo_url`, `get_apt_config`, `sources_list_dir`, `add_repository`, and `install_key`. It embeds a full PGP public key block and uses `apt-key add`.

Control flow: On `configure`, it installs the embedded key and writes `cryfs.list` into the apt sources parts directory with either Debian/Devuan or Ubuntu repository URL based on `lsb_release`. Unsupported distributions print a warning and exit successfully. Abort cases no-op; unknown arguments fail.

State and persistence behavior: Persists an APT trusted key and a `cryfs.list` package source file under the system apt configuration. It does not run `apt-get update`; it only configures future package source availability.

Dependencies and integration points: Registered through `CPACK_DEBIAN_PACKAGE_CONTROL_EXTRA`. Depends on `bash`, `lsb_release`, `apt-config`, `apt-key`, and Debian-family apt layout.

Risks: Uses HTTP repository URLs and deprecated global `apt-key`, increasing security and modernization concerns. The script writes to apt source parts without quoting all variables. Unsupported distributions leave users on manual updates. The embedded key must be rotated in-package if CryFS repository signing changes.

Test signals: Package install on Debian/Ubuntu should leave a `cryfs.list` with the right codename and a trusted key. Unknown maintainer-script argument should fail.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/cpack/debfiles/postinst` completely for this pass (124 lines, 4814 bytes).
