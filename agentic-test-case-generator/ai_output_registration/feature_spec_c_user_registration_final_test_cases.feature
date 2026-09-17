Feature: User Registration

@CUR_TC_001 @positive @p0
Scenario: Successful registration with valid data
  Given User is on registration page
  When Enter valid email
  And Enter valid password
  And Click Register
  Then Account created; Success message displayed

@CUR_TC_002 @negative @p0
Scenario: Duplicate email submission
  Given Email already exists in DB
  When Enter existing email
  And Enter valid password
  And Click Register
  Then Error: 'Email already registered'

@CUR_TC_003 @negative @p1
Scenario: Empty required fields validation
  Given User is on registration page
  When Leave email blank
  And Leave password blank
  And Click Register
  Then Inline validation errors shown; No API request sent

@CUR_TC_004 @boundary @p1
Scenario: Password minimum length (8 chars)
  Given User is on registration page
  When Enter valid email
  And Enter 8-char password
  And Click Register
  Then Account created

@CUR_TC_005 @boundary @p1
Scenario: Password maximum length (64 chars)
  Given User is on registration page
  When Enter valid email
  And Enter 64-char password
  And Click Register
  Then Account created

@CUR_TC_006 @negative @p1
Scenario: Password too short (7 chars)
  Given User is on registration page
  When Enter valid email
  And Enter 7-char password
  And Click Register
  Then Validation error: Password must be 8-64 chars

@CUR_TC_007 @negative @p1
Scenario: Password too long (65 chars)
  Given User is on registration page
  When Enter valid email
  And Enter 65-char password
  And Click Register
  Then Validation error: Password must be 8-64 chars

@CUR_TC_008 @negative @p1
Scenario: Invalid email format
  Given User is on registration page
  When Enter invalid email
  And Enter valid password
  And Click Register
  Then Error: 'Enter a valid email address.'

@CUR_TC_009 @edge @p2
Scenario: Email with special characters
  Given User is on registration page
  When Enter email with + symbol
  And Enter valid password
  And Click Register
  Then Account created (if valid RFC 5322)

@CUR_TC_010 @positive @p2
Scenario: Registration with mixed case email
  Given User is on registration page
  When Enter mixed case email
  And Enter valid password
  And Click Register
  Then Account created; Email stored as provided or normalized
