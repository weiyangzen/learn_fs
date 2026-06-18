# sources/user-network-fs/samba/source4/torture/rap/sam.c

Purpose: This file builds the RAP SAM torture sub-suite, covering user password changes, user information retrieval, user creation, and user deletion through legacy RAP calls.

Important APIs, types, and functions: `samr_rand_pass()` generates random passwords. Password tests use `rap_NetUserPasswordSet2` in clear and DES-hash modes, and `rap_NetOEMChangePassword` with RC4-encrypted password buffers. Other tests use `rap_NetUserGetInfo`, `rap_NetUserAdd`, and `rap_NetUserDelete`. `torture_rap_sam()` registers the sub-suite.

Control flow: Password tests create a temporary domain user with `torture_create_testuser_max_pwlen()`, run password-change calls, update the local password only when the RAP status is OK, and leave the domain. OEM password change builds old/new DES hashes, encodes the new password buffer, encrypts it with ARCFOUR keyed by the old hash, and computes the old-password-hash verifier. User getinfo creates a user, queries levels 0, 1, 2, 10, and 11, then removes the user. User add verifies duplicate add returns `WERR_NERR_USEREXISTS`, then deletes. User delete creates a user, deletes it, and verifies the second delete returns `WERR_NERR_USERNOTFOUND`.

State and persistence behavior: The tests mutate domain SAM state by creating, changing, and deleting `torture_rap_user`. Cleanup is explicit through `torture_leave_domain()` or RAP delete, but failures can leave the test user behind or changed.

Dependencies and integration points: The file depends on RAP client calls, Samba torture domain join helpers, random password generation, legacy auth helpers `E_deshash`, `E_old_pw_hash`, `encode_pw_buffer`, GnuTLS ARCFOUR, and domain/workgroup settings.

Risks: It requires privileges to create users and change passwords. It prints generated passwords to output, which is acceptable in torture logs but sensitive in general logs. Password length limits and legacy encryption behavior are fragile across server policy changes.

Test signals: Passing tests show RAP SAM operations, password encoding/encryption paths, duplicate/not-found error mapping, and multi-level user info marshalling operate correctly.
