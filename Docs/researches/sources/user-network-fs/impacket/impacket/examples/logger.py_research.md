# sources/user-network-fs/impacket/impacket/examples/logger.py

## Purpose
`logger.py` centralizes example-script logging configuration for Impacket. It adds a root `StreamHandler` with Impacket-specific prefixes and optional timestamps, supports ntlmrelayx identity prefixes, and sets the logging level for normal or debug output.

## Important APIs, Types, and Functions
- `ImpacketFormatter` formats records as `bullet identity message`, mapping INFO to `[*]`, DEBUG to `[+]`, WARNING to `[!]`, and errors/others to `[-]`.
- `ImpacketFormatterTimeStamp` extends that format with a timestamp and formats time as `%Y-%m-%d %H:%M:%S`.
- `init(ts=False, debug=False)` installs the handler, adds `IdentityFilter`, sets root level to DEBUG or INFO, logs the installation path in debug mode, and silences `impacket.smbserver` down to ERROR in non-debug mode.

## Control Flow
Callers invoke `init()` early in a script. The function constructs a `logging.StreamHandler(sys.stdout)`, selects a formatter based on `ts`, attaches the identity filter, adds it to the root logger, and adjusts logger levels.

## State and Persistence Behavior
The function mutates global logging state by adding handlers to the root logger. Repeated calls add additional handlers because no deduplication is performed. Formatter methods mutate transient `LogRecord` attributes `bullet` and `identity`.

## Dependencies and Integration Points
It depends on Python `logging`, `sys`, `impacket.version`, and `impacket.examples.ntlmrelayx.utils.identity_log.IdentityFilter`. It is used by Impacket command-line examples to get consistent console output.

## Risks and Edge Cases
Repeated initialization can duplicate log lines. Formatting assumes root records can safely receive dynamic attributes. The identity filter dependency couples generic example logging to ntlmrelayx utility code.

## Test Signals
Tests should assert prefix mapping by level, timestamp rendering, identity preservation/defaulting, root logger level changes, smbserver logger suppression in non-debug mode, and duplicate handler behavior on repeated `init()` calls.
