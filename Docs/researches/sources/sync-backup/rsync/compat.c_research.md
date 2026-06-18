# sources/sync-backup/rsync/compat.c

## Purpose
Centralizes protocol compatibility negotiation for rsync peers, including protocol version exchange, feature flags, incremental recursion eligibility, checksum/compression name negotiation, daemon-auth digest negotiation, file-list extra indexes, and old-protocol option constraints.

## Important APIs, Types, and Functions
Exports global negotiation state such as `remote_protocol`, `file_extra_cnt`, `inc_recurse`, `compat_flags`, `use_safe_inc_flist`, `want_xattr_optim`, `proper_seed_order`, `inplace_partial`, `do_negotiated_strings`, and file-extra indexes. `setup_protocol()` is the main entrypoint. `set_allow_inc_recurse()` gates incremental recursion. `parse_compress_choice()`, `get_nni_by_name()`, `get_nni_by_num()`, `get_default_nno_list()`, `validate_choice_vs_env()`, and the static negotiate helpers implement named algorithm negotiation. `output_daemon_greeting()` and `negotiate_daemon_auth()` support rsyncd startup. `get_subprotocol_version()` hides pre-release subprotocols from older protocol choices.

## Control Flow
`setup_protocol()` first assigns file-list extra slots based on selected preservation options, exchanges protocol numbers when needed, validates min/max compatibility, applies old-protocol restrictions, chooses delete timing defaults, sends or reads protocol 30+ compatibility flags, finalizes incremental recursion and symlink/iconv/xattr/varint capabilities, injects partial-dir filters, negotiates checksum and compression strings, exchanges checksum seed, finalizes checksum/compression choices, selects the xattr checksum, emits batch shell metadata, and initializes file-list internals.

## State and Persistence Behavior
This file mutates process-global capability state that downstream sender, receiver, generator, file-list, xattr, checksum, compression, batch, and filter code consumes. It reads environment variables `RSYNC_COMPRESS_LIST` and `RSYNC_CHECKSUM_LIST` to constrain algorithm negotiation. It persists no files itself except indirectly through write-batch setup.

## Dependencies and Integration Points
Depends on `valid_checksums`, `valid_auth_checksums`, compression constants, option globals, filter parsing, batch helpers, checksum initialization, `init_flist()`, and daemon greeting code used by `clientserver.c`. Its file-extra indexes must match file-list serialization/deserialization code.

## Risks and Test Signals
Risks include incompatible feature flags, protocol downgrade mistakes, mismatched checksum/compression lists, environment restrictions that reject valid explicit choices, batch files produced with different capabilities, and incorrect file-extra ordering. Test signals include protocol matrix transfers against older rsyncs, daemon auth negotiation, `--checksum-choice`/`--compress-choice` with environment lists, protocol 29/30/31 option boundaries, batch read/write tests, crtimes rejection without varint flags, and incremental recursion disabled by incompatible delete/delay/prune options.
