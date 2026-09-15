Feature: User Login

@LOGIN_TC_001 @positive @p0 @AC1
Scenario: Successful login with valid active user
  Given Registered active user exists and dashboard is available
  When Open login page
  And Enter registered email
  And Enter correct password
  And Click Log In
  Then User is redirected to dashboard.

@LOGIN_TC_002 @positive @p0 @AC1 @AC8
Scenario: Successful login establishes session
  Given Registered active user exists
  When Log in using valid credentials
  And Inspect authenticated state or session cookie/token
  Then Authenticated session is created and user can access dashboard resources.

@LOGIN_TC_003 @negative @p0 @AC2
Scenario: Wrong password shows generic error
  Given Registered active user exists
  When Open login page
  And Enter registered email
  And Enter wrong password
  And Click Log In
  Then Error "Invalid email or password" is shown and user remains on login page.

@LOGIN_TC_004 @negative @p1 @AC3
Scenario: Unregistered email shows generic error
  Given Email address is not registered
  When Open login page
  And Enter unregistered email
  And Enter any valid-format password
  And Click Log In
  Then Same generic error "Invalid email or password" is shown with no account-existence indication.

@LOGIN_TC_005 @negative @p1 @AC4
Scenario: Blank email prevents login request
  Given Login page is open
  When Leave Email blank
  And Enter password
  And Click Log In
  Then Required-field validation is shown for Email and no login request is sent.

@LOGIN_TC_006 @negative @p1 @AC4
Scenario: Blank password prevents login request
  Given Login page is open
  When Enter valid email
  And Leave Password blank
  And Click Log In
  Then Required-field validation is shown for Password and no login request is sent.

@LOGIN_TC_007 @negative @p1 @AC4
Scenario: Both email and password blank
  Given Login page is open
  When Leave Email blank
  And Leave Password blank
  And Click Log In
  Then Required-field validation is shown for both fields and no login request is sent.

@LOGIN_TC_008 @negative @p1 @AC5
Scenario: Invalid email without at-sign is rejected
  Given Login page is open
  When Enter malformed email
  And Enter password
  And Click Log In
  Then Inline message "Enter a valid email address" is shown.

@LOGIN_TC_009 @negative @p2 @AC5
Scenario: Invalid email without domain is rejected
  Given Login page is open
  When Enter malformed email
  And Enter password
  And Click Log In
  Then Inline message "Enter a valid email address" is shown.

@LOGIN_TC_010 @negative @p2 @AC5
Scenario: Invalid email with spaces is rejected
  Given Login page is open
  When Enter email containing internal spaces
  And Enter password
  And Click Log In
  Then Inline message "Enter a valid email address" is shown.

@LOGIN_TC_011 @boundary @p0 @AC6
Scenario: Four failed attempts do not lock account
  Given Registered active user exists; failed-attempt counter is zero
  When Attempt login four times with wrong password within 15 minutes
  And Attempt fifth login with correct password
  Then User is not locked after four failures and valid login succeeds.

@LOGIN_TC_012 @boundary @p0 @AC6
Scenario: Fifth failed attempt locks account
  Given Registered active user exists; failed-attempt counter is zero
  When Attempt login five times with wrong password within 15 minutes
  Then Account is locked and message "Your account is locked. Try again later." is shown.

@LOGIN_TC_013 @edge @p0 @AC6
Scenario: Correct credentials during lockout remain blocked
  Given Account is locked due to five failed attempts
  When Enter correct email and correct password
  And Click Log In
  Then Login is denied and locked message is shown.

@LOGIN_TC_014 @boundary @p0 @AC6
Scenario: Failed attempts outside 15-minute window do not lock account
  Given Registered active user exists; failed-attempt counter is zero
  When Make four failed attempts
  And Wait more than 15 minutes
  And Make one failed attempt
  Then Account is not locked because failures are not five consecutive attempts within 15 minutes.

@LOGIN_TC_015 @boundary @p0 @AC6
Scenario: Login allowed after 30-minute lockout expires
  Given Account locked at T0
  When Wait at least 30 minutes after lockout
  And Enter correct credentials
  And Click Log In
  Then User can log in successfully after lockout period ends.

@LOGIN_TC_016 @positive @p1 @AC7
Scenario: Email matching is case-insensitive
  Given Registered active user exists with lowercase email
  When Enter email with different case
  And Enter correct password
  And Click Log In
  Then Login succeeds and user is redirected to dashboard.

@LOGIN_TC_017 @negative @p0 @AC7
Scenario: Password matching is case-sensitive
  Given Registered active user exists
  When Enter correct email
  And Enter password with changed letter case
  And Click Log In
  Then Login fails with "Invalid email or password".

@LOGIN_TC_018 @positive @p0 @AC8
Scenario: Refresh keeps authenticated user logged in
  Given User has successfully logged in
  When Navigate to dashboard
  And Refresh browser
  Then User remains logged in and dashboard reloads successfully.

@LOGIN_TC_019 @boundary @p0 @AC8
Scenario: Session expires after 24 hours
  Given User has successfully logged in
  When Keep session idle or simulate time until 24 hours expires
  And Refresh dashboard or access protected resource
  Then Session is expired and user must log in again.

@LOGIN_TC_020 @positive @p1 @AC8
Scenario: Logout ends session before expiry
  Given User has successfully logged in
  When Click Log Out
  And Try to access dashboard
  And Refresh browser
  Then User is logged out and dashboard access redirects to login page.

@LOGIN_TC_021 @negative @p0 @AC9
Scenario: Inactive account cannot log in
  Given Registered user account is deactivated
  When Enter inactive account email
  And Enter correct password
  And Click Log In
  Then Message "This account is inactive. Contact support." is shown and no session is created.

@LOGIN_TC_022 @edge @p2 @AC4 @AC5
Scenario: Blank email shows required message instead of format message
  Given Login page is open
  When Leave Email blank
  And Enter password
  And Click Log In
  Then Required-field validation is shown, not email-format validation.

@LOGIN_TC_023 @edge @p0 @AC6 @AC2
Scenario: Lockout message takes precedence after threshold
  Given Account reaches five failed attempts
  When Attempt an additional login with wrong password after lockout
  Then Message "Your account is locked. Try again later." is shown instead of generic password error.

@LOGIN_TC_024 @boundary @p1 @AC2 @AC6
Scenario: Minimum length valid password authenticates when correct
  Given Registered user has an 8-character password
  When Enter registered email
  And Enter correct 8-character password
  And Click Log In
  Then Login succeeds if password is correct and account is active.

@LOGIN_TC_025 @boundary @p1 @AC2 @AC6
Scenario: Maximum length valid password authenticates when correct
  Given Registered user has a 64-character password
  When Enter registered email
  And Enter correct 64-character password
  And Click Log In
  Then Login succeeds if password is correct and account is active.

@LOGIN_TC_026 @edge @p1 @AC3 @AC7
Scenario: Unregistered email with mixed case still returns generic error
  Given Email does not exist in any case variation
  When Enter mixed-case unregistered email
  And Enter any password
  And Click Log In
  Then Generic error "Invalid email or password" is shown.

@LOGIN_TC_027 @positive @p1 @AC1 @AC8
Scenario: Dashboard directly accessible after login
  Given User has logged in successfully
  When After login, navigate directly to dashboard URL
  Then Dashboard is accessible without re-entering credentials.

@LOGIN_TC_028 @edge @p0 @AC9 @AC6
Scenario: Inactive account does not enter lockout flow
  Given Inactive registered account exists
  When Attempt login for inactive account multiple times with correct password
  Then Inactive-account message is shown, user is not logged in, and behavior does not reveal lockout-specific state.
