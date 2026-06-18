# sources/test-tools/crashmonkey/code/utils/utils.h

Purpose: declares utility structures for block-level disk write logs and replay data slices. These are lower-level than `DiskMod`, representing actual write operations captured from the disk wrapper.

Important APIs/types/functions: class `disk_write`, `disk_write_op_meta metadata`, flag/query methods, static `serialize`/`deserialize`, data ownership methods, equality/stream operators, and struct `DiskWriteData` with `full_bio`, indexes, offset, size, and `GetData`.

Control flow: no implementation in the header; callers construct writes, classify them into epochs, serialize logs, and pass `DiskWriteData` into replay paths. State/persistence behavior: `disk_write` owns optional write payload through `shared_ptr<char>`, while `DiskWriteData` shares a larger buffer.

Dependencies/integration: includes `disk_wrapper_ioctl.h` and is used by permuter and utils tests. Risks/test signals: comments warn pointer lifetime depends on object lifetime, and metadata struct has C layout with manual initialization in constructors.
