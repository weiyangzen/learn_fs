# File Research: sources/local-fs/erofs-utils/lib/remotes/docker_config.c

This file implements Docker `config.json` credential lookup when json-c is available, and stubs it out with `-EOPNOTSUPP` otherwise.

Without json-c:
- `erofs_docker_config_lookup()` returns `-EOPNOTSUPP`.
- `erofs_docker_credential_free()` is a no-op.

With json-c:
- `docker_config_path()` resolves `$DOCKER_CONFIG/config.json`, or `$HOME/.docker/config.json`.
- `read_file_to_string()` reads config files up to 4 MiB.
- `registry_match()` treats Docker Hub specially: `docker.io` and `registry-1.docker.io` match `https://index.docker.io/v1/`; other registries match case-insensitively by exact key.
- `decode_auth_field()` base64-decodes `username:password`, splits on the first colon, duplicates both strings, and scrubs the decoded buffer.
- `erofs_docker_config_lookup()` parses JSON, scans `auths`, decodes the matching `auth` field, and returns populated credentials.
- `erofs_docker_credential_free()` scrubs and frees username/password.

Important behavior:
- Missing config, missing auths, or no matching registry returns `-ENOENT`.
- Malformed JSON returns `-EINVAL`.
- Sensitive buffers are cleared with `erofs_free_sensitive()` where implemented.

Risk / note:
- Only inline `auth` entries are supported; external credential helpers/stores are not handled.
