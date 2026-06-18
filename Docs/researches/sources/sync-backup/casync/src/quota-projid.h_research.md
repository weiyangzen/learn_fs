# sources/sync-backup/casync/src/quota-projid.h

Purpose: public interface for Linux project quota ID helpers.

Important APIs/types/functions: declares `read_quota_projid(int fd, uint32_t *ret)` and `write_quota_projid(int fd, uint32_t id)`.

Control flow/state: no state in the header; all persistence is filesystem metadata addressed by fd.

Dependencies/integration: includes integer types and is compiled only where Linux quota ioctls are available through the implementation.

Risks/test signals: callers must be prepared for `-ENOTTY`, `-EOPNOTSUPP`, or permission failures. Extraction logic should treat unsupported project IDs according to feature flags rather than blindly failing portability cases.

Source research group: `subset-b-009122`.
