<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/config/url_config.go -->
# sources/sync-backup/git-lfs/config/url_config.go

## Research

`url_config.go` implements Git’s URL-scoped config matching for keys such as `http.<url>.<key>` and `credential.<url>.<key>`. `URLConfig.Get`, `GetAll`, and `Bool` search URL-specific keys first and fall back to `<prefix>.<key>`. `getAll` parses all config keys, compares scheme, host/wildcard host, port, path prefix, and optional username, then chooses the highest-scoring match.

Supporting helpers include `portForURL`, `compareHosts`, `comparePaths`, `hostsAndPaths`, `hosts`, `paths`, and `isDefaultLFSUrl`, which treats `/repo.git/info/lfs` as matching `/repo`. State is just the wrapped Git environment. Integration is used by credentials and HTTP/LFS API configuration. Risks include regex matching over raw config keys, URL parse failures silently producing fallback behavior, wildcard host scoring, path score precedence over username only after host, and special `.git/info/lfs` matching edge cases. `url_config_test.go` covers roots, users, ports, HTTP vs HTTPS, SSH ports, wildcards, and `.git` default LFS URLs.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/config/url_config.go -->
