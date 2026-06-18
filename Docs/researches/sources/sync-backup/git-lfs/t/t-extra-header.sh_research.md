# sources/sync-backup/git-lfs/t/t-extra-header.sh

## Purpose

Verifies that Git HTTP `extraHeader` settings are copied to Git LFS HTTP requests, including multiple headers, authorization headers, non-standard authorization casing, and mixed-case URL/config-key lookup.

## Important APIs, control flow, and dependencies

The tests use `setup_remote_repo`, `clone_repo`, `git config --add http.<url>.extraHeader`, `git config --add http.extraHeader`, `git lfs track`, `git push`, `GIT_CURL_VERBOSE=1`, and `GIT_TRACE=1`. Credential-required repositories use a Basic Authorization header built with `base64`. Mixed-case tests configure `http.<Git URL>.ExtraHeader` and verify it applies to the derived LFS URL.

## State, dependencies, integration points, risks, and test signals

State includes local Git config, remote URL-derived LFS endpoint selection, committed LFS object data, and credential helper side effects. Integration points are Git URL config matching, LFS API extra-header injection, header casing treatment, auth bypass when Authorization is supplied, and trace/curl logging. Risks include lowercasing too much of the URL, ignoring multiple headers, invoking credential helpers despite Authorization headers, or mishandling `AUTHORIZATION` casing. Signals are verbose curl header greps and zero counts for credential fill/approve/cache/reject trace lines.
