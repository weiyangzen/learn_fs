# File Research: sources/local-fs/ocfs2-tools/o2cb_ctl/jconfig.c

GLib-backed parser, editor, iterator source, and dumper for the stanza-based O2CB config format.

The parser accepts stanza headers of the form `name:` at column one, attribute lines starting with whitespace and using `key = value`, comments beginning with `#`, blank-line stanza separation, and continuation lines ending in backslash. It records parse errors in `JConfigCtxt` and can parse from files, stdin, or memory.

The in-memory model supports duplicate stanzas with the same name, attribute lookup/set/delete, filtered stanza iteration with `JConfigMatch`, and dumping back to file or memory with multiline attributes escaped. Notable code concern: `j_config_parse_to_eol()` uses assignment in `if ((token = G_TOKEN_CHAR) && ...)`, which still depends on `value->v_char` but does not actually compare the token type.
