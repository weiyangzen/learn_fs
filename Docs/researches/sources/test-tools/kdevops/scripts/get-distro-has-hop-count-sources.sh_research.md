<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/get-distro-has-hop-count-sources.sh -->
# sources/test-tools/kdevops/scripts/get-distro-has-hop-count-sources.sh

Purpose: checks whether the first configured Debian package source is within an acceptable traceroute hop count, returning `y` or `n`. It supports legacy `sources.list` and DEB822 `debian.sources`.

Important APIs and functions: no shell functions. It reads optional acceptable hop count argument, checks `/etc/debian_version`, selects a sources file, extracts the first repository host, runs `traceroute -n -w 1,1,1`, computes line count minus one, and compares with the threshold.

Control flow: non-Debian, missing sources, missing traceroute, empty host, or excessive hops all return `n`; acceptable hop count returns `y`.

State and persistence: read-only against `/etc` and network path; no writes.

Dependencies and integration: bash, grep, awk, sed, cut, traceroute. Used by `Kconfig.guestfs`, `Kconfig.distro`, and devconfig mirror checks to infer local mirror suitability.

Risks: host extraction only considers the first source and may mis-handle complex DEB822 files with multiple `URIs:`. `traceroute` line count can include failures or DNS behavior despite `-n`. Unquoted variables risk path/URL whitespace issues. Test signals include containerized fixture parsing for both source formats, missing traceroute behavior, and stubbed traceroute output.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/get-distro-has-hop-count-sources.sh -->
