# sources/test-tools/kdevops/scripts/check_nix_mirror.sh

Purpose: Kconfig helper for Nix cache mirror availability and URL detection.

Important APIs/types/functions: `check_http_mirror`, `check_local_mirror`, `curl --connect-timeout`, `find` for `.narinfo`/`.nar`, `hostname -I`, and case outputs for use/availability/URL.

Control flow: reports mirror use if local cache or HTTP endpoint exists, reports availability for HTTP endpoint, returns an HTTP localhost/host-IP URL when reachable, falls back to `file://` local path, or prints empty/`n`.

State/persistence behavior: read-only filesystem and HTTP inspection.

Dependencies/integration: used by Nix/NixOS kdevops mirror configuration.

Risks/test signals: local directory is treated as configured even if empty; URL detection uses first host IP. Test signals are `y/n` and usable cache URL.
