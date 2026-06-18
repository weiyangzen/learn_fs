# sources/test-tools/kdevops/playbooks/python/workflows/fstests/augment_expunge_list.py

Purpose: Scans fstests result trees for `.bad` and `.dmesg` failures and augments expunge-list files for oscheck/fstests reruns.

Key APIs and flow: `main()` loads top-level `.config`, walks the results tree, derives hostname/kernel/section/group/test from path layout, builds `group/test` failure lines, chooses an expunge output path, creates missing directories, appends new failures only once, and finally calls `sort-expunges.sh`. Helpers parse kconfig-like booleans and append lines.

State, dependencies, integration: Mutates expunge directories under the requested output root and shells out to the kdevops sort script. It depends on `.config`, filesystem layout conventions, and optional openSUSE/KOTD settings.

Risks and test signals: Path parsing is positional; `base_kernel` is referenced after conditional initialization when kernels do not end with `+`; duplicate detection is substring-like; disabled legacy branch remains. Tests should cover new set creation, existing file append, base-kernel fallback, openSUSE shortcuts, and malformed result paths.
