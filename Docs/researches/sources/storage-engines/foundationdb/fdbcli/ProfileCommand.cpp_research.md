# sources/storage-engines/foundationdb/fdbcli/ProfileCommand.cpp

Purpose: Implements `profile` commands for client transaction profiling settings and listing worker process addresses.

Important APIs/types/functions: `profileCommandActor(Database, Reference<ITransaction>, tokens, intrans)`, `db->globalConfig`, global config keys `fdbClientInfoTxnSampleRate` and `fdbClientInfoTxnSizeLimit`, `GlobalConfig::prefixedKey`, `Tuple::makeTuple`, `parse_with_suffix`, and worker-interface range reads.

Control flow: `profile client get` waits for global config initialization, reads sample rate and size limit from the in-memory global config with sentinel defaults, and prints current settings. `profile client set <RATE|default> <SIZE|default>` parses rate with `strtod` or infinity sentinel, parses size with suffix parser or `-1`, enables special-key writes, writes packed tuple values to global config keys, and commits if not inside a transaction. `profile list` scans worker interface special keys and prints IP:port addresses with `:tls` stripped. Invalid type/action/arity prints errors.

State and persistence behavior: Client profiling settings are persisted through global configuration special keys. `profile list` is read-only. In transaction mode, writes are staged but not committed by this actor.

Dependencies and integration points: Depends on global config, tuple encoding, fdbcli transaction mode, worker-interface special keys, and client profiling consumers that observe the global keys.

Risks: `strtod` validation checks for whitespace after the parsed rate; tokens may not be null-terminated in all contexts, so this parsing pattern merits scrutiny. It does not check sample-rate range or size-limit overflow beyond helper behavior. `profile list` asserts no `more` result.

Test signals: Cover get defaults and explicit values, set defaults, numeric rate/size suffix parsing, invalid rate/size, in-transaction staging, worker list TLS stripping, and malformed worker-interface range size.
