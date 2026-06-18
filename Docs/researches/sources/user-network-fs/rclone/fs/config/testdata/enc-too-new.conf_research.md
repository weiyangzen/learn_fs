<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/testdata/enc-too-new.conf -->
# sources/user-network-fs/rclone/fs/config/testdata/enc-too-new.conf

## Purpose
Fixture for encrypted config load failure when the encryption version marker is newer than the loader supports.

## Important APIs, Types, And Control Flow
The file is shaped like an encrypted config but uses `RCLONE_ENCRYPT_V1:` rather than the supported V0 marker. Tests set this as the config path and expect load failure.

## State And Persistence
Static fixture with no runtime mutation.

## Dependencies And Integration Points
Connects encrypted config parser version checks to public load behavior.

## Risks And Test Signals
Good signal for forward-version rejection. It does not validate a future migration path, only fail-fast behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/testdata/enc-too-new.conf -->
