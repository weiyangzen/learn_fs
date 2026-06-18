## sources/test-tools/kdevops/workflows/fstests/osfiles/ubuntu/helpers.sh

Purpose: Provides Ubuntu oscheck hooks, including optional installation of missing fstests dependencies for Ubuntu 18.04, known expunges, skip groups, ypbind restart, and distro-kernel detection.

Important APIs/types/functions: Functions include `install_basic_reqs`, `ubuntu_install_*`, `ubuntu_read_osfile`, `ubuntu_special_expunges`, `ubuntu_skip_groups`, `ubuntu_restart_ypbind`, and `ubuntu_distro_kernel_check`.

Control flow: Install helpers funnel most required tools through `install_basic_reqs`; fio, dbench, setcap, and setfattr have focused package installs. Release 18.04 receives older XFS expunges and broad XFS skip groups.

State and persistence: May persist package changes through `apt-get install` when oscheck requests missing requirement remediation. Also mutates expunge and skip variables.

Dependencies and integration points: Loaded dynamically by oscheck. Depends on `apt-get`, `lsb_release`, `dpkg -S`, and common oscheck helper functions.

Risks and test signals: Package installation is narrowly coded for 18.04, so newer Ubuntu releases may only emit a suggestion. Test with `FSTESTS_SETUP_SYSTEM=y oscheck.sh --check-deps` and verify dependency remediation behavior.
