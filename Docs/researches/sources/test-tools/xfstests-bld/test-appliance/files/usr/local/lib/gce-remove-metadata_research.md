# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-remove-metadata

Purpose: small concurrency-safe wrapper for removing metadata keys from the current GCE instance.

Important flow: source `gce-funcs`, create `/run/xattr.lock` if absent, and use `flock` to serialize `gcloud compute instances -q remove-metadata --zone $ZONE $(hostname) --keys "$@"`.

State and dependencies: persistent state is only the lock file. It depends on `gcloud`, `$ZONE`, hostname matching the instance name, and write access to GCE metadata.

Integration points: complements `gce-add-metadata` and scripts that coordinate through metadata keys such as status, shutdown reasons, and LTM wait signals.

Risks and test signals: all arguments are passed as one comma/key string to `--keys`; callers must provide valid key syntax. Failures are redirected to `/dev/null`, so tests should verify metadata side effects rather than logs.
