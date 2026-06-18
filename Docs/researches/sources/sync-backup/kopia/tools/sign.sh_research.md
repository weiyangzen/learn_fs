# sources/sync-backup/kopia/tools/sign.sh

Purpose: signs Kopia release artifacts by adding RPM signatures, regenerating `dist/checksums.txt`, and creating a detached GPG signature for the checksum file.

Control flow/APIs: loops over `dist/*rpm` and runs `rpm --define "%_gpg_name Kopia Builder" --addsign`. Then it reads filenames from the existing checksum file, regenerates checksums inside `dist`, and writes `dist/checksums.txt.sig` via `gpg --detach-sig`.

State/persistence: mutates RPM files in place by signing them, rewrites `dist/checksums.txt`, and writes `dist/checksums.txt.sig`.

Dependencies/integration: bash, RPM signing configuration, GPG key setup, `sha256sum`, and a populated `dist` directory. Used at the release-signing stage before publishing.

Risks/test signals: assumes `dist/checksums.txt` exists and contains filenames matching current dist artifacts. Only RPMs are modified before checksum regeneration. Failure halfway can leave some RPMs signed and checksum/signature stale. Verification is external: `rpm --checksig`, `sha256sum -c`, and GPG signature checks.
