# sources/security-integrity/selinux/libsemanage/src/semanage_conf.h

Purpose: declares the parsed libsemanage configuration structure and parser/destructor APIs.

Important types/APIs: `semanage_conf_t` holds store type/path/root, compiler directory, server port, policy version, target platform, booleans for expansion/save/cache/relabel behavior, unknown handling, file mode, bzip settings, ignored directories for genhomedircon, external program lists, and module output program paths. `external_prog_t` is a linked list of path/args commands. APIs are `semanage_conf_parse` and `semanage_conf_destroy`.

Control flow/integration: handle creation parses this config and later code reads fields for direct store selection, compiler path construction, genhomedircon behavior, setfiles/sefcontext_compile invocations, and module cache policy.

State/persistence: the parsed config is heap-owned by `semanage_handle_t` and destroyed with the handle. Risks include ownership of many string fields and linked lists, defaults when options are absent, and keeping struct fields synchronized with parser and sample config. Test signals include parser default values, destroy leak checks, ignoredirs propagation, and external program list parsing.
