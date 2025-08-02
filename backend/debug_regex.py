#!/usr/bin/env python3
"""
Debug script for regex pattern matching
"""

import re

def test_regex_patterns():
    """Test different regex patterns for extracting summary and is_mult"""
    
    # Test cases with different JSON formats
    test_cases = [
        # Case 1: Simple JSON
        '''{
          "aircraft_registration": "N123AB",
          "aircraft_make_model": "Cessna 172",
          "summary": "Multiple maintenance entries including tire replacement and engine inspection",
          "is_mult": true,
          "log_entries": []
        }''',
        
        # Case 2: JSON with newlines in summary
        '''{
          "aircraft_registration": "N123AB",
          "aircraft_make_model": "Cessna 172",
          "summary": "Multiple maintenance entries including tire replacement and engine inspection with detailed work performed",
          "is_mult": true,
          "log_entries": []
        }''',
        
        # Case 3: Truncated JSON (simulating the actual issue)
        '''{
          "aircraft_registration": "N123AB",
          "aircraft_make_model": "Cessna 172",
          "summary": "Multiple maintenance entries including tire replacement and engine inspection",
          "is_mult": true,
          "log_entries": [
            {
              "description_of_work_performed": "Replaced left main landing gear tire",
              "tach_time": "1250.5",
              "hobbs_time": "1250.5",
              "part_number_replaced": ["Tire-123", "Tube-456"],
              "manual_reference": "Aircraft Maintenance Manual Chapter 32",
              "reason_for_maintenance": "Scheduled maintenance",
              "ad_compliance": "AD 2023-15-02 complied with",
              "next_due_compliance": "Next inspection due in 50 hours",
              "service_bulletin_reference": "SB 2023-01",
              "certification_statement": "I certify that this aircraft is airworthy",
              "performed_by": "John Smith",
              "license_number": "A&P 123456",
              "date": "2024-01-15",
              "risk_level": "Low",
              "urgency": "Normal",
              "is_airworthy": true
            }
          ]
        }''',
        
        # Case 4: JSON with escaped quotes in summary
        '''{
          "aircraft_registration": "N123AB",
          "aircraft_make_model": "Cessna 172",
          "summary": "Multiple maintenance entries including tire replacement and engine inspection with \"special\" requirements",
          "is_mult": true,
          "log_entries": []
        }'''
    ]
    
    # Test different regex patterns
    patterns = [
        # Pattern 1: Original pattern
        (r'"summary"\s*:\s*"([^"]*)"', "Original pattern"),
        
        # Pattern 2: With DOTALL flag
        (r'"summary"\s*:\s*"([^"]*)"', "With DOTALL flag"),
        
        # Pattern 3: More robust pattern
        (r'"summary"\s*:\s*"((?:[^"\\]|\\.)*)"', "Robust pattern"),
        
        # Pattern 4: Simple pattern for is_mult
        (r'"is_mult"\s*:\s*(true|false)', "Is_mult pattern")
    ]
    
    for i, test_json in enumerate(test_cases, 1):
        print(f"\n=== Test Case {i} ===")
        print(f"JSON preview: {test_json[:200]}...")
        
        for pattern, description in patterns:
            print(f"\n--- Testing {description} ---")
            print(f"Pattern: {pattern}")
            
            if "is_mult" in pattern:
                # Test is_mult pattern
                match = re.search(pattern, test_json)
                print(f"Match found: {match is not None}")
                if match:
                    print(f"Extracted value: {match.group(1)}")
            else:
                # Test summary pattern
                if "DOTALL" in description:
                    match = re.search(pattern, test_json, re.DOTALL)
                else:
                    match = re.search(pattern, test_json)
                print(f"Match found: {match is not None}")
                if match:
                    print(f"Extracted summary: {match.group(1)}")
                    print(f"Summary length: {len(match.group(1))}")

if __name__ == "__main__":
    test_regex_patterns() 