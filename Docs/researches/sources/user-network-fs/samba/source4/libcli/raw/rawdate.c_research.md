<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/rawdate.c -->
# sources/user-network-fs/samba/source4/libcli/raw/rawdate.c

Purpose: `rawdate.c` is a thin adapter around Samba DOS date conversion helpers. It ensures raw SMB client packet encoders and parsers consistently use the negotiated server timezone stored in `smbcli_transport`.

Important APIs, types, and functions: The file exports `raw_push_dos_date`, `raw_push_dos_date2`, `raw_push_dos_date3`, `raw_pull_dos_date`, `raw_pull_dos_date2`, and `raw_pull_dos_date3`. These call lower-level `push_dos_date*` and `pull_dos_date*` helpers with `transport->negotiate.server_zone`.

Control flow: Each push function receives a Unix `time_t`, a target buffer, and an offset, then writes the corresponding SMB DOS date layout. Each pull function receives a pointer to wire date bytes and returns a GMT Unix `time_t` adjusted from the server zone. The three variants match SMB wire formats with different word order or 32-bit "Unix-like" DOS timestamp layout.

State and persistence behavior: No state is stored. The only state read is `transport->negotiate.server_zone`, populated during negotiation. The functions mutate caller-provided packet buffers for outgoing requests.

Dependencies and integration points: Raw file open/close, read/write-close, metadata, and search parsers call these helpers for legacy SMB date fields. They depend on negotiate having recorded server time zone accurately. NTTIME fields use separate helpers in `rawrequest.c`; this file is for DOS date formats.

Risks: Timestamp correctness depends on negotiation data and legacy DOS date semantics, including local-time conversion and DST behavior. Using the wrong variant (`date`, `date2`, or `date3`) swaps word order or format and can produce plausible but wrong timestamps. These functions assume valid buffer space at the supplied offset.

Test signals: Raw open, qfileinfo, search, delay-write, and setfileinfo torture tests indirectly validate timestamp round-trips. Targeted tests should compare servers in non-UTC time zones, boundary dates, zero timestamps, and operations that mix DOS time and NTTIME fields.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/rawdate.c -->
