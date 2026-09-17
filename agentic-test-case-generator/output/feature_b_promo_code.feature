Feature: Apply Promo Code at Checkout

@PROMO_TC_001 @positive @p0 @AC1
Scenario: Apply SAVE10 to ₹1000 subtotal
  Given Cart subtotal is ₹1000 and SAVE10 is active
  When Enter SAVE10
  And Click Apply
  Then Discount of ₹100 is applied to item subtotal and order total updates.

@PROMO_TC_002 @positive @p0 @AC2
Scenario: Apply FLAT200 to ₹1500 subtotal
  Given Cart subtotal is ₹1500 and FLAT200 is active
  When Enter FLAT200
  And Click Apply
  Then Discount of ₹200 is applied and total updates.

@PROMO_TC_003 @negative @p0 @AC3
Scenario: Reject FLAT200 below minimum
  Given Cart subtotal is ₹800
  When Enter FLAT200
  And Click Apply
  Then Message "This code requires a minimum order of ₹1000." is shown and total is unchanged.

@PROMO_TC_004 @boundary @p0 @AC3
Scenario: Accept FLAT200 exactly at minimum
  Given Cart subtotal is exactly ₹1000
  When Enter FLAT200
  And Click Apply
  Then Code is accepted and ₹200 discount is applied.

@PROMO_TC_005 @boundary @p1 @AC3
Scenario: Reject FLAT200 just below minimum
  Given Cart subtotal is ₹999
  When Enter FLAT200
  And Click Apply
  Then Minimum-order error is shown and total is unchanged.

@PROMO_TC_006 @negative @p0 @AC4
Scenario: Expired code is rejected
  Given Promo code EXPIRED10 exists but validity window has ended
  When Enter expired code
  And Click Apply
  Then Message "This code has expired." is shown and total is unchanged.

@PROMO_TC_007 @negative @p1 @AC5
Scenario: Non-existent code is rejected
  Given Cart is on checkout page
  When Enter unknown code
  And Click Apply
  Then Message "Invalid promo code." is shown and total is unchanged.

@PROMO_TC_008 @positive @p1 @AC6
Scenario: Lowercase save10 behaves like SAVE10
  Given Cart subtotal is ₹1000 and SAVE10 is active
  When Enter save10
  And Click Apply
  Then Discount of ₹100 is applied identically to SAVE10.

@PROMO_TC_009 @positive @p2 @AC6
Scenario: Mixed-case Save10 behaves like SAVE10
  Given Cart subtotal is ₹1000 and SAVE10 is active
  When Enter Save10
  And Click Apply
  Then Discount of ₹100 is applied identically to SAVE10.

@PROMO_TC_010 @negative @p0 @AC7
Scenario: Already redeemed single-use code is rejected
  Given Customer has previously redeemed ONCE100
  When Enter ONCE100
  And Click Apply
  Then Message "This code has already been used." is shown and total is unchanged.

@PROMO_TC_011 @boundary @p0 @AC8
Scenario: Fixed discount is capped at subtotal
  Given Cart subtotal is ₹150 and FLAT200 variant has no minimum
  When Enter FLAT200_NOMIN
  And Click Apply
  Then Discounted subtotal becomes ₹0 and never negative.

@PROMO_TC_012 @boundary @p0 @AC8
Scenario: Fixed discount equal to subtotal results in zero subtotal
  Given Cart subtotal is ₹200 and fixed discount is ₹200
  When Enter FLAT200_NOMIN
  And Click Apply
  Then Discounted subtotal is exactly ₹0.

@PROMO_TC_013 @positive @p1 @AC9
Scenario: Confirm replacing existing code applies only new code
  Given SAVE10 already applied to cart
  When Enter FLAT200
  And Click Apply
  And Confirm replacement
  Then SAVE10 is removed and only FLAT200 discount applies.

@PROMO_TC_014 @negative @p1 @AC9
Scenario: Cancel replacing existing code keeps old code
  Given SAVE10 already applied to cart
  When Enter FLAT200
  And Click Apply
  And Cancel replacement prompt
  Then SAVE10 remains applied and FLAT200 is not applied.

@PROMO_TC_015 @negative @p1 @AC10
Scenario: Empty promo input is rejected
  Given Checkout page is open
  When Leave promo input blank
  And Click Apply
  Then Message "Enter a promo code." is shown.

@PROMO_TC_016 @positive @p2 @AC11
Scenario: Leading and trailing spaces are trimmed
  Given Cart subtotal is ₹1000 and SAVE10 is active
  When Enter code with spaces
  And Click Apply
  Then Spaces are trimmed and SAVE10 discount is applied.

@PROMO_TC_017 @positive @p2 @AC11 @AC6
Scenario: Trim spaces and normalize lowercase code
  Given Cart subtotal is ₹1000 and SAVE10 is active
  When Enter lowercase code with spaces
  And Click Apply
  Then Code is trimmed, matched case-insensitively, and ₹100 discount is applied.

@PROMO_TC_018 @edge @p0 @AC12
Scenario: Applied minimum code removed when subtotal drops below minimum
  Given FLAT200 is applied to cart subtotal ₹1500
  When Remove item so subtotal becomes ₹800
  Then Promo is revalidated, discount is removed, and code is no longer eligible.

@PROMO_TC_019 @positive @p1 @AC12
Scenario: Applied minimum code remains when subtotal stays eligible
  Given FLAT200 is applied to cart subtotal ₹1500
  When Remove item so subtotal becomes ₹1200
  Then Promo remains applied and total recalculates with ₹200 discount.

@PROMO_TC_020 @boundary @p1 @AC1
Scenario: Percentage discount on small subtotal rounds consistently
  Given SAVE10 active and cart subtotal is ₹99
  When Enter SAVE10
  And Click Apply
  Then 10% subtotal discount is calculated using application rounding rules and total updates.

@PROMO_TC_021 @edge @p1 @AC1
Scenario: Percentage discount applies to subtotal only, not shipping
  Given Cart has subtotal ₹1000 and shipping charge exists
  When Enter SAVE10
  And Click Apply
  Then Discount is ₹100 on subtotal only; shipping is not discounted.

@PROMO_TC_022 @edge @p0 @AC1
Scenario: Taxes calculated on discounted subtotal
  Given Cart subtotal is ₹1000 with tax calculation enabled
  When Enter SAVE10
  And Click Apply
  And Review tax amount
  Then Tax is calculated on ₹900 discounted subtotal, not ₹1000.

@PROMO_TC_023 @edge @p0 @AC2
Scenario: Fixed discount affects taxable subtotal
  Given Cart subtotal is ₹1500 with tax calculation enabled
  When Enter FLAT200
  And Click Apply
  And Review tax amount
  Then Tax is calculated on ₹1300 discounted subtotal.

@PROMO_TC_024 @boundary @p1 @AC4
Scenario: Code valid at start of validity window is accepted
  Given Current time equals code validity start
  When Enter windowed active code
  And Click Apply
  Then Code is accepted if usage and cart rules are satisfied.

@PROMO_TC_025 @boundary @p1 @AC4
Scenario: Code rejected after validity end
  Given Current time is after code validity end
  When Enter expired code
  And Click Apply
  Then Expired-code message is shown and total is unchanged.

@PROMO_TC_026 @negative @p2 @AC5 @AC11
Scenario: Whitespace-only input is treated as empty
  Given Checkout page is open
  When Enter spaces only
  And Click Apply
  Then After trimming, message "Enter a promo code." is shown.

@PROMO_TC_027 @negative @p1 @AC9
Scenario: Second invalid code does not replace existing valid code
  Given SAVE10 already applied
  When Enter invalid second code
  And Click Apply
  Then Invalid promo code message is shown and SAVE10 remains applied.

@PROMO_TC_028 @negative @p1 @AC9 @AC3
Scenario: Second ineligible code does not replace existing code
  Given SAVE10 already applied and subtotal is ₹800
  When Enter FLAT200
  And Click Apply
  Then Minimum-order error is shown and existing SAVE10 remains applied unless valid replacement is confirmed.

@PROMO_TC_029 @edge @p0 @AC7 @AC9
Scenario: Already-used replacement code is rejected
  Given SAVE10 already applied; ONCE100 was redeemed earlier
  When Enter ONCE100
  And Click Apply
  Then Already-used message is shown and existing code remains unchanged.

@PROMO_TC_030 @edge @p0 @AC12
Scenario: Promo discount recalculates when subtotal increases
  Given SAVE10 applied to subtotal ₹1000
  When Add item so subtotal becomes ₹2000
  Then Discount recalculates from ₹100 to ₹200 and total updates.

@PROMO_TC_031 @edge @p0 @AC8 @AC12
Scenario: Capped fixed discount recalculates after cart change
  Given Fixed ₹200 no-minimum code applied to subtotal ₹150
  When Add item so subtotal becomes ₹300
  Then Discount recalculates to ₹200 and discounted subtotal becomes ₹100.

@PROMO_TC_032 @negative @p2 @AC10 @AC11
Scenario: Empty input does not clear existing promo
  Given SAVE10 is already applied
  When Clear promo input
  And Click Apply
  Then Message "Enter a promo code." is shown and existing applied discount remains unchanged.

@PROMO_TC_033 @negative @p2 @AC5
Scenario: Unsupported characters in code rejected as invalid
  Given Checkout page is open
  When Enter code containing unsupported symbols
  And Click Apply
  Then Message "Invalid promo code." is shown and total is unchanged.

@PROMO_TC_034 @edge @p0 @AC1 @AC2 @AC9
Scenario: Discounts are not stacked when replacing code
  Given SAVE10 applied to ₹1500 subtotal
  When Enter FLAT200
  And Confirm replacement
  And Review summary
  Then Only ₹200 discount is applied; previous ₹150 SAVE10 discount is removed and not stacked.
