#!/usr/bin/env python3
"""
Minimal test script to debug the summary field issue
"""

import re
import json

def test_summary_extraction():
    """Test summary extraction from JSON"""
    
    # Simulate a truncated JSON response
    json_str = '''{
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
}'''
    
    print("=== Testing Summary Extraction ===")
    print(f"JSON string length: {len(json_str)}")
    print(f"JSON preview: {json_str[:200]}...")
    
    # Check if fields are present
    has_summary = '"summary"' in json_str
    has_is_mult = '"is_mult"' in json_str
    print(f"Has summary: {has_summary}")
    print(f"Has is_mult: {has_is_mult}")
    
    # Find positions
    summary_pos = json_str.find('"summary"')
    is_mult_pos = json_str.find('"is_mult"')
    print(f"Summary position: {summary_pos}")
    print(f"Is_mult position: {is_mult_pos}")
    
    # Test regex patterns
    patterns = [
        r'"summary"\s*:\s*"([^"]*)"',
        r'"summary"\s*:\s*"([^"]*)"',
        r'"summary"\s*:\s*"((?:[^"\\]|\\.)*)"',
    ]
    
    for i, pattern in enumerate(patterns):
        print(f"\n--- Testing pattern {i+1}: {pattern} ---")
        match = re.search(pattern, json_str, re.DOTALL)
        print(f"Match found: {match is not None}")
        if match:
            print(f"Extracted summary: {match.group(1)}")
    
    # Test is_mult pattern
    is_mult_pattern = r'"is_mult"\s*:\s*(true|false)'
    is_mult_match = re.search(is_mult_pattern, json_str)
    print(f"\n--- Testing is_mult pattern: {is_mult_pattern} ---")
    print(f"Match found: {is_mult_match is not None}")
    if is_mult_match:
        print(f"Extracted is_mult: {is_mult_match.group(1)}")
    
    # Test manual extraction
    print(f"\n--- Testing manual extraction ---")
    if summary_pos != -1:
        # Find the colon after "summary"
        colon_pos = json_str.find(':', summary_pos)
        if colon_pos != -1:
            # Find the opening quote
            quote_start = json_str.find('"', colon_pos)
            if quote_start != -1:
                # Find the closing quote
                quote_end = json_str.find('"', quote_start + 1)
                if quote_end != -1:
                    summary = json_str[quote_start + 1:quote_end]
                    print(f"Manually extracted summary: {summary}")
    
    if is_mult_pos != -1:
        # Find the colon after "is_mult"
        colon_pos = json_str.find(':', is_mult_pos)
        if colon_pos != -1:
            # Find the value (true or false)
            value_start = colon_pos + 1
            while value_start < len(json_str) and json_str[value_start].isspace():
                value_start += 1
            if value_start < len(json_str):
                if json_str.startswith('true', value_start):
                    print(f"Manually extracted is_mult: true")
                elif json_str.startswith('false', value_start):
                    print(f"Manually extracted is_mult: false")

if __name__ == "__main__":
    test_summary_extraction() 