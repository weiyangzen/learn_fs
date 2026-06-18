# sources/user-network-fs/nfs-utils/tests/statdb_dump.c

Purpose: `statdb_dump.c` dumps statd NSM monitor/notify database records in a stable text format for tests.

Important APIs and control flow: A callback passed to `nsm_load_monitor_list` or `nsm_load_notify_list` formats host, timestamp, address, program/version/procedure, cookie hex, mon_name, and my_name. `main` sets up pathnames from arguments and selects monitor or notify database dumping.

State, dependencies, and integration: It reads statd state directories through `support/nsm/file.c` APIs. Static buffers hold cookie and address formatting. It integrates with shell tests that compare statd side effects.

Risks and test signals: Output stability depends on timestamp and address formatting. Tests should cover empty DBs, malformed records, IPv4 address formatting, cookie conversion, monitor versus notify directory selection, and non-default state directories.
