<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/pam_cifscreds.c -->
# sources/user-network-fs/cifs-utils/pam_cifscreds.c

## Purpose

`pam_cifscreds.c` implements a PAM module that captures a user's authentication token and stores CIFS credential keys in the session keyring when a PAM session opens, with update support on password change.

## Important APIs, Types, and Functions

Important functions are `parse_args`, `free_password`, `cleanup_free_password`, `cifscreds_pam_add`, `cifscreds_pam_update`, `pam_sm_authenticate`, `pam_sm_open_session`, `pam_sm_close_session`, `pam_sm_setcred`, and `pam_sm_chauthtok`. It uses argument flags `ARG_DOMAIN` and `ARG_DEBUG`.

## Control Flow

`pam_sm_authenticate` parses module args, obtains PAM user and `PAM_AUTHTOK`, and stores a duplicated password in PAM data with a cleanup scrubber. `pam_sm_open_session` retrieves that password, requires a `host=` or `domain=` argument, checks the session keyring, and calls `cifscreds_pam_add`. Add/update paths validate host/domain and username, resolve host addresses unless domain mode is set, search for existing keys, and add or update `logon` keys using `key_add`. `pam_sm_chauthtok` updates existing credentials during `PAM_UPDATE_AUTHTOK`.

## State and Persistence Behavior

PAM data holds a duplicated password until cleanup. Credential persistence is in keyutils session keyring keys with `DEFAULT_KEY_TIMEOUT`. The password cleanup function overwrites memory before free.

## Dependencies and Integration Points

It depends on PAM headers, keyutils, resolver helpers, `cifskey.h`, `mount.h`, and `util.h`. It integrates with PAM service configuration that supplies `host=` or `domain=`, and with `pam_keyinit` for session keyrings.

## Risks and Edge Cases

`parse_args` can leave `hostdomain` unset if no host/domain is provided; callers must enforce this. `cifscreds_pam_update` counts existing keys but then loops using `currentaddress` after the scan has advanced it to NULL, so update appears unable to update the actual matched addresses. Existing-key behavior in add returns a service error rather than refreshing. PAM applications that do not preserve module data across callbacks will skip key setup.

## Test Signals

PAM integration tests should cover authenticate/open-session sequencing, host and domain modes, missing host/domain, duplicate keys, password cleanup, missing session keyring, password-change update behavior, and the suspected update-address bug.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/pam_cifscreds.c -->
