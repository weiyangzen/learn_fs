## sources/security-integrity/acl/tools/parse.h

Purpose: public parser contract for ACL tool command sequences.

It defines parse-mode bits `SEQ_PARSE_WITH_PERM`, `SEQ_PARSE_NO_PERM`, `SEQ_PARSE_MULTI`, `SEQ_PARSE_DEFAULT`, and `SEQ_PROMOTE_ACL`, then declares the text and stream parsers used by `setfacl.c`. The API integrates with `sequence.h` by returning or appending `cmd_t` objects and with restore logic by exposing comment metadata outputs for path, uid, gid, and mode flags. State is owned by callers except allocated `path_p` from `read_acl_comments`. Risks are mode-bit combinations that can make permissions optional and the need for callers to free comment paths. Tests should exercise both inline CLI ACL strings and multi-line restore input.
