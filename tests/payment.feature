ANALYSIS:
1. Variables: Amount, Currency, User Status
2. Rules: Min 10, VIP=95%, Bank API.

SCENARIOS:
Feature: Payment Processing

  Scenario: Valid Payment
    Given User is Standard
    And Amount is 20
    When Processed
    Then Charged should be 19.00 (5% discount)

  Scenario: Insufficient Funds
    Given Amount is 9
    Then Error "Min amount 10" should appear

  Scenario: VIP Discount
    Given User is VIP
    And Amount is 20
    When Processed
    Then Charged should be 19.00 (5% discount)

  Scenario: Bank API Failure
    Given Amount is 20
    But Bank API fails to connect
    Then Error "Bank timeout" should appear