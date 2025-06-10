Feature: Patients API
  Scenario: List patients
    Given the dicomweb proxy is running in Docker
    When I request "/patients"
    Then the response code should be 200

