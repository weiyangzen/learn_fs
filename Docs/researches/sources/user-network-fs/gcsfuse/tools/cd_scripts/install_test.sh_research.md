<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/cd_scripts/install_test.sh -->
# sources/user-network-fs/gcsfuse/tools/cd_scripts/install_test.sh

Purpose: Release installation test script that verifies the to-be-released gcsfuse package installs, older version installation works, and package manager upgrade returns to the latest release.

Important APIs, types, and functions: Shell flow installs Python 3.11 locally for gcloud compatibility, upgrades gcloud, reads release details from `gs://gcsfuse-release-packages/version-detail/details.txt`, configures apt/yum repositories, installs exact gcsfuse version, checks `gcsfuse --version`, removes it, installs old version `1.2.0`, upgrades, compares versions with `sort -V`, and uploads logs/success marker.

Control flow: After dependency setup and gcloud upgrade, OS detection via `details.txt` and VM name selects Debian/Ubuntu or RHEL/CentOS package manager logic. Debian path handles apt-key vs signed-by behavior based on VM name; RHEL path writes a yum repo file. Any logged "Failure" suppresses success marker upload.

State and persistence behavior: Installs build dependencies and Python under `$HOME/.local`, modifies package repositories, installs/removes/upgrades system `gcsfuse`, writes logs in home, and uploads artifacts to the release bucket.

Dependencies and integration points: Depends on gcloud, GCE metadata, release bucket details format, package repositories, apt/yum, Python source download, and package availability for version `1.2.0`.

Risks and test signals: String comparisons on VM names for apt-key policy are fragile. Python source build is slow and network-dependent. Some package install output redirection precedence may only redirect fallback commands. Test signal is `success.txt` plus logs uploaded under `installation-test/<vm>`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/cd_scripts/install_test.sh -->
