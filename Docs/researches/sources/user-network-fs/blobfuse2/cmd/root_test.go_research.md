# sources/user-network-fs/blobfuse2/cmd/root_test.go
## sources/user-network-fs/blobfuse2/cmd/root_test.go

Purpose: validates top-level command behavior, version metadata probing, and fstab-style argument normalization.

Important APIs/helpers: `rootCmdSuite`, `osArgs`, `executeCommandC` from `mountv1_test.go`, `getDummyVersion`, and `cleanupTest`. Setup installs a silent logger; cleanup clears `rootCmd` output/error/args.

Control flow: tests execute `rootCmd` with no args and with `--disable-version-check`, expecting the missing command message. HTTP tests call `checkVersionExists` against invalid URLs and live `common.GitHubReleaseBaseURL` sentinel paths for security warnings, blocked versions, and absent latest metadata. `TestDetectNewVersionCurrentOlder` temporarily overrides `common.Blobfuse2Version`, reads from `beginDetectNewVersion`, and expects an upgrade message. `TestParseArgs` feeds synthetic `os.Args` strings through `parseArgs` and compares the normalized argument string.

State and persistence: mutates global `common.Blobfuse2Version` in one test and restores it. Uses global `rootCmd` and logger state. No persistent file outputs.

Dependencies/integration: depends on live internet access to raw GitHub metadata for several tests, so CI behavior may vary with network and metadata state. It also depends on Cobra command registrations from package init.

Risks: tests that assert remote sentinel files for version `1.1.1` are brittle if repository metadata changes or network calls fail. Channel receive from `beginDetectNewVersion` assumes the goroutine sends a value; a latest-version path with no send could deadlock if re-enabled incorrectly. Shared command state requires cleanup discipline.

Test signals: gives direct coverage of root argument compatibility for `/etc/fstab` forms and validates the newer raw-file version-check strategy.
